import logging
import requests
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, delete
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from fastapi import HTTPException

from app.core.config import settings
from app.db import models
from app.schemas.acao import TickerCreate, TickerUpdate
from app.schemas.grafico import GraficoDataOut, GraficoComparativoOut, GraficoDataset

def _valida_ticker_externamente(ticker_code: str) -> bool:
    logging.info(f"Validando ticker '{ticker_code}' externamente...")
    url = f"https://statusinvest.com.br/acoes/{ticker_code}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def create_ticker(db: Session, ticker_data: TickerCreate) -> models.Ticker:
    ticker_upper = ticker_data.codigo.upper()
    if not _valida_ticker_externamente(ticker_upper):
        raise HTTPException(status_code=400, detail=f"Ticker '{ticker_upper}' não encontrado ou inválido na fonte de dados externa.")
    
    stmt_exists = select(models.Ticker).where(models.Ticker.codigo == ticker_upper)
    if db.execute(stmt_exists).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Ticker já cadastrado.")
    
    new_ticker = models.Ticker(**ticker_data.model_dump())
    new_ticker.codigo = ticker_upper
    db.add(new_ticker)
    db.commit()
    db.refresh(new_ticker)
    return new_ticker

def get_dados_completos_acao(db: Session, ticker_code: str) -> Optional[Tuple[models.Ticker, models.HistoricoAcao]]:
    stmt_ticker = select(models.Ticker).where(models.Ticker.codigo == ticker_code.upper())
    ticker_info = db.execute(stmt_ticker).scalar_one_or_none()
    if not ticker_info:
        return None

    stmt_historico = select(models.HistoricoAcao).where(models.HistoricoAcao.ticker_codigo == ticker_code.upper()).order_by(desc(models.HistoricoAcao.date)).limit(1)
    ultimo_historico = db.execute(stmt_historico).scalar_one_or_none()
    if not ultimo_historico:
        return None

    data_registro = datetime.combine(ultimo_historico.date, datetime.now().time())
    if data_registro < datetime.now() - timedelta(minutes=settings.DATA_MAX_AGE_MINUTES):
        logging.warning(f"Dados para {ticker_code} estão desatualizados.")
        return None

    return ticker_info, ultimo_historico

def get_todos_os_tickers(db: Session) -> list[models.Ticker]:
    return db.execute(select(models.Ticker).order_by(models.Ticker.codigo)).scalars().all()

def get_eventos_por_ticker(db: Session, ticker: str) -> Optional[list[models.EventoCorporativo]]:
    if not db.execute(select(models.Ticker).where(models.Ticker.codigo == ticker.upper())).scalar_one_or_none():
        return None
    stmt = select(models.EventoCorporativo).where(models.EventoCorporativo.ticker_codigo == ticker.upper()).order_by(desc(models.EventoCorporativo.data_com))
    return db.execute(stmt).scalars().all()

def get_principais_indices(db: Session) -> list[models.Indice]:
    return db.execute(select(models.Indice).where(models.Indice.nome.in_(["IBOV", "IFIX"]))).scalars().all()

def delete_acao_by_ticker(db: Session, ticker_code: str) -> Optional[models.Ticker]:
    stmt_ticker = select(models.Ticker).where(models.Ticker.codigo == ticker_code.upper())
    db_ticker = db.execute(stmt_ticker).scalar_one_or_none()
    if not db_ticker:
        return None

    db.execute(delete(models.HistoricoAcao).where(models.HistoricoAcao.ticker_codigo == ticker_code.upper()))
    db.execute(delete(models.EventoCorporativo).where(models.EventoCorporativo.ticker_codigo == ticker_code.upper()))
    db.delete(db_ticker)
    db.commit()
    return db_ticker

def get_dados_para_grafico(db: Session, ticker_code: str) -> Optional[GraficoDataOut]:
    if not db.execute(select(models.Ticker).where(models.Ticker.codigo == ticker_code.upper())).scalar_one_or_none():
        return None
    
    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=90)
    stmt = select(models.HistoricoAcao.date, models.HistoricoAcao.close).where(models.HistoricoAcao.ticker_codigo == ticker_code.upper(), models.HistoricoAcao.date.between(data_inicio, data_fim)).order_by(models.HistoricoAcao.date.asc())
    resultados = db.execute(stmt).all()
    if not resultados:
        return GraficoDataOut(labels=[], data=[])

    labels = [res.date.strftime('%d/%m') for res in resultados]
    data = [res.close for res in resultados]
    return GraficoDataOut(labels=labels, data=data)

def get_dados_grafico_comparativo(db: Session, dias: int = 90) -> GraficoComparativoOut:
    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=dias)
    stmt = select(models.HistoricoAcao.date, models.HistoricoAcao.ticker_codigo, models.HistoricoAcao.close).where(models.HistoricoAcao.date.between(data_inicio, data_fim)).order_by(models.HistoricoAcao.date.asc())
    resultados = db.execute(stmt).all()

    if not resultados:
        return GraficoComparativoOut(labels=[], datasets=[])

    df = pd.DataFrame(resultados, columns=['date', 'ticker', 'close'])
    df = df.drop_duplicates(subset=['date', 'ticker'], keep='last')
    
    df_pivot = df.pivot(index='date', columns='ticker', values='close')
    df_pivot = df_pivot.ffill()
    df_pivot = df_pivot.apply(pd.to_numeric, errors='coerce')
    df_pivot = df_pivot.dropna(axis='columns') 

    if df_pivot.empty:
        return GraficoComparativoOut(labels=[], datasets=[])

    df_normalized = (df_pivot / df_pivot.iloc[0] - 1) * 100
    df_normalized.index = pd.to_datetime(df_normalized.index)
    labels = df_normalized.index.strftime('%Y-%m-%d').tolist()
    
    datasets = [GraficoDataset(label=ticker, data=df_normalized[ticker].round(2).tolist()) for ticker in df_normalized.columns]
    return GraficoComparativoOut(labels=labels, datasets=datasets)

def update_ticker_nome(db: Session, ticker_code: str, ticker_update: TickerUpdate) -> Optional[models.Ticker]:
    """
    Encontra um ticker pelo seu código e atualiza seu nome.
    """
    stmt = select(models.Ticker).where(models.Ticker.codigo == ticker_code.upper())
    db_ticker = db.execute(stmt).scalar_one_or_none()

    if not db_ticker:
        return None 

    db_ticker.nome = ticker_update.nome
    
    db.commit()
    db.refresh(db_ticker)
    
    return db_ticker