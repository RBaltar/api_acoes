from pydantic import BaseModel
from datetime import datetime

class ColetaLogOut(BaseModel):
    id: int
    timestamp: datetime
    status: str
    mensagem: str

    class Config:
        from_attributes = True