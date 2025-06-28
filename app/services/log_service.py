from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from typing import List

from app.db import models

def get_coleta_logs(db: Session, limit: int = 100) -> List[models.ColetaLog]:
    """Busca os últimos logs de coleta, ordenados por mais recente."""
    stmt = select(models.ColetaLog).order_by(desc(models.ColetaLog.timestamp)).limit(limit)
    return db.execute(stmt).scalars().all()