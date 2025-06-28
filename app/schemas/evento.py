from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Optional

class EventoCorporativoOut(BaseModel):
    tipo_evento: str
    data_com: date
    data_pagamento: Optional[date]
    valor: Optional[Decimal]

    class Config:
        from_attributes = True