from fastapi import Security, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from ..core.config import settings
from ..db import models, database
from sqlalchemy import select

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_current_user(
    api_key: str = Security(api_key_header),
    db: Session = Depends(database.get_db)
) -> models.Usuario:
    if not settings.API_SAFE_MODE:
        return models.Usuario(id=0, nome="dev_user", email="dev@test.com", api_key="dev_key", ativo=True)

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de API (X-API-Key) não fornecida."
        )
        
    stmt = select(models.Usuario).where(models.Usuario.api_key == api_key, models.Usuario.ativo == True)
    user = db.scalars(stmt).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chave de API inválida ou usuário inativo."
        )
    return user