from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal
import datetime

class AcaoBase(BaseModel):
    ticker: str = Field(..., max_length=10, description="Ticker da ação (ex: PETR4).")
    nome_empresa: str
    preco_atual: Decimal
    variacao_percentual: Decimal
    atualizado_em: datetime.datetime

class AcaoOut(AcaoBase):
    class Config:
        from_attributes  = True

class MultiAcoesOut(BaseModel):
    acoes_encontradas: List[AcaoOut]
    acoes_nao_encontradas: List[str]

class TickerInfoOut(BaseModel):
    codigo: str
    nome: str

    class Config:
        from_attributes = True

class TickerCreate(BaseModel):
    codigo: str = Field(..., max_length=10, description="Código do ticker (ex: PETR4).")
    nome: str = Field(..., max_length=100, description="Nome da empresa.")

class TickerUpdate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100, description="O novo nome da empresa.")