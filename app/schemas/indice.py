from pydantic import BaseModel
from decimal import Decimal
import datetime

class IndiceOut(BaseModel):
    nome: str
    valor_atual: Decimal
    variacao_dia: Decimal
    atualizado_em: datetime.datetime

    class Config:
        from_attributes = True