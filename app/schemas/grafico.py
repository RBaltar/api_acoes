from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal

class GraficoDataOut(BaseModel):
    labels: List[str] 
    data: List[Decimal]

class GraficoDataset(BaseModel):
    label: str
    data: List[float]

class GraficoComparativoOut(BaseModel):
    labels: List[str]
    datasets: List[GraficoDataset] = Field(..., description="Conjunto de dados para cada ticker")