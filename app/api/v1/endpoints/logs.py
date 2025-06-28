from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.log import ColetaLogOut
from app.services import log_service

router = APIRouter()

@router.get("/coleta", response_model=List[ColetaLogOut], summary="Listar Logs de Coleta")
def read_coleta_logs(db: Session = Depends(get_db)):
    """Retorna os últimos 100 logs gerados pelo script de coleta de dados."""
    return log_service.get_coleta_logs(db)