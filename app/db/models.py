from sqlalchemy import (Column, String, Numeric, TIMESTAMP, Integer, ForeignKey,
                        Date, Boolean, Text, BigInteger)
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Ticker(Base):
    __tablename__ = "tickers"
    
    id = Column(Integer, primary_key=True)
    nome = Column(Text, nullable=False)
    codigo = Column(Text, nullable=False, unique=True, index=True)

    historico = relationship("HistoricoAcao", back_populates="ticker_info")


class HistoricoAcao(Base):
    __tablename__ = "acoes_historico"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker_codigo = Column("ticker", Text, ForeignKey("tickers.codigo"), nullable=False)
    
    date = Column(Date, nullable=False)
    close = Column(Numeric, nullable=False)
    variacao_percentual = Column(Numeric(6, 2), nullable=True)
    price_earnings = Column(Numeric)
    dividend_yield = Column(Numeric)
    roe = Column(Numeric)
    market_value = Column(Numeric)
    volume = Column(BigInteger) 

    ticker_info = relationship("Ticker", back_populates="historico")


class Indice(Base):
    __tablename__ = "indices"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, index=True)
    valor_atual = Column(Numeric(10, 2))
    variacao_dia = Column(Numeric(6, 2))
    atualizado_em = Column(TIMESTAMP, default=datetime.datetime.utcnow)

class LogRequisicao(Base):
    __tablename__ = "logs_requisicoes"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    endpoint = Column(String(255))
    method = Column(String(10))
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    timestamp = Column(TIMESTAMP, default=datetime.datetime.utcnow)

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50))
    email = Column(String(100), unique=True)
    api_key = Column(String(100), unique=True)
    ativo = Column(Boolean, default=True)

class EventoCorporativo(Base):
    __tablename__ = "eventos_corporativos"
    id = Column(Integer, primary_key=True, index=True)
    ticker_codigo = Column(Text, ForeignKey("tickers.codigo"), nullable=False, index=True)
    tipo_evento = Column(String(50), nullable=False) 
    data_com = Column(Date, nullable=False) 
    data_pagamento = Column(Date, nullable=True) 
    valor = Column(Numeric(10, 4), nullable=True) 
    ticker = relationship("Ticker")

class ColetaLog(Base):
    __tablename__ = "coleta_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    status = Column(String(50), default="INFO")
    mensagem = Column(Text)