from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.db.database import get_db
from app.schemas.acao import AcaoOut, MultiAcoesOut, TickerInfoOut, TickerCreate, TickerUpdate
from app.schemas.indice import IndiceOut
from app.schemas.msg import Msg
from app.schemas.evento import EventoCorporativoOut
from app.schemas.grafico import GraficoDataOut, GraficoComparativoOut
from app.services import acao_service
from app.core.security import get_current_user
from app.db.models import Usuario

router = APIRouter()

@router.post("/", response_model=TickerInfoOut, status_code=status.HTTP_201_CREATED, summary="Cadastrar um novo Ticker")
def create_new_ticker(ticker_data: TickerCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return acao_service.create_ticker(db=db, ticker_data=ticker_data)

@router.get("/listar-todos", response_model=List[TickerInfoOut], summary="Listar todos os Tickers cadastrados")
def list_all_tickers(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    tickers_list = acao_service.get_todos_os_tickers(db=db)
    return [TickerInfoOut.model_validate(t, from_attributes=True) for t in tickers_list]

@router.get("/buscar", response_model=MultiAcoesOut, summary="Consultar dados de Múltiplas Ações")
def read_multi_acoes(tickers: List[str] = Query(..., min_length=1, description="Lista de tickers"), db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    acoes_encontradas = []
    acoes_nao_encontradas = []
    for ticker_code in tickers:
        dados = acao_service.get_dados_completos_acao(db, ticker_code)
        if dados:
            ticker_info, ultimo_historico = dados
            data_e_hora_atualizacao = datetime.combine(ultimo_historico.date, datetime.min.time())
            acao_out = AcaoOut(ticker=ticker_info.codigo, nome_empresa=ticker_info.nome, preco_atual=ultimo_historico.close, variacao_percentual=ultimo_historico.variacao_percentual or 0.0, atualizado_em=data_e_hora_atualizacao)
            acoes_encontradas.append(acao_out)
        else:
            acoes_nao_encontradas.append(ticker_code)
    return {"acoes_encontradas": acoes_encontradas, "acoes_nao_encontradas": acoes_nao_encontradas}

@router.get("/grafico-comparativo", response_model=GraficoComparativoOut, summary="Obter dados para gráfico comparativo")
def get_comparative_chart_data(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return acao_service.get_dados_grafico_comparativo(db=db)

@router.get("/indices/principais", response_model=List[IndiceOut], summary="Consultar Principais Índices")
def read_indices(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    indices = acao_service.get_principais_indices(db=db)
    if not indices:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Índices não encontrados.")
    return indices

@router.get("/{ticker}", response_model=AcaoOut, summary="Consultar dados de uma Ação")
def read_acao(ticker: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    dados = acao_service.get_dados_completos_acao(db=db, ticker_code=ticker)
    if dados is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticker '{ticker}' ou seu histórico não encontrados.")
    ticker_info, ultimo_historico = dados
    data_e_hora_atualizacao = datetime.combine(ultimo_historico.date, datetime.min.time())
    return AcaoOut(ticker=ticker_info.codigo, nome_empresa=ticker_info.nome, preco_atual=ultimo_historico.close, variacao_percentual=ultimo_historico.variacao_percentual or 0.0, atualizado_em=data_e_hora_atualizacao)

@router.get("/{ticker}/grafico", response_model=GraficoDataOut, summary="Obter dados para gráfico")
def get_chart_data(ticker: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    dados_grafico = acao_service.get_dados_para_grafico(db=db, ticker_code=ticker)
    if dados_grafico is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticker '{ticker}' não encontrado.")
    return dados_grafico

@router.get("/{ticker}/eventos", response_model=List[EventoCorporativoOut], summary="Consultar eventos corporativos")
def read_acao_eventos(ticker: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    eventos = acao_service.get_eventos_por_ticker(db=db, ticker=ticker)
    if eventos is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticker '{ticker}' não encontrado.")
    return eventos
    
@router.delete("/{ticker}", response_model=Msg, summary="Deletar uma Ação")
def delete_acao(ticker: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    deleted_ticker = acao_service.delete_acao_by_ticker(db=db, ticker_code=ticker)
    if deleted_ticker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ação com ticker '{ticker}' não encontrada.")
    return {"detail": f"Ação '{ticker}' e seus dados relacionados foram deletados com sucesso."}

@router.put(
    "/{ticker}",
    response_model=TickerInfoOut,
    summary="Atualizar o nome de uma Ação",
    responses={404: {"model": Msg, "description": "Ação não encontrada."}}
)
def update_ticker(
    ticker: str,
    ticker_update_data: TickerUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza o nome de uma ação (ticker) já existente no sistema.
    """
    updated_ticker = acao_service.update_ticker_nome(
        db=db, 
        ticker_code=ticker, 
        ticker_update=ticker_update_data
    )
    
    if updated_ticker is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ação com ticker '{ticker}' não encontrada para atualização."
        )
    
    return updated_ticker
