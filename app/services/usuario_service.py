import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from fastapi import HTTPException, status

from app.db import models
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

def get_usuario(db: Session, user_id: int) -> Optional[models.Usuario]:
    """Busca um único usuário pelo seu ID."""
    return db.get(models.Usuario, user_id)

def get_usuario_by_email(db: Session, email: str) -> Optional[models.Usuario]:
    """Busca um único usuário pelo seu email."""
    stmt = select(models.Usuario).where(models.Usuario.email == email)
    return db.execute(stmt).scalar_one_or_none()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100) -> List[models.Usuario]:
    """Busca todos os usuários com paginação."""
    stmt = select(models.Usuario).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()

def create_usuario(db: Session, user: UsuarioCreate) -> models.Usuario:
    """Cria um novo usuário e gera uma chave de API única."""
    if get_usuario_by_email(db, email=user.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado.")
    
    api_key_unica = str(uuid.uuid4())
    db_user = models.Usuario(
        email=user.email,
        nome=user.nome,
        api_key=api_key_unica
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print(f"Novo usuário criado: {db_user.email}, Chave API: {db_user.api_key}") # Log útil no terminal
    return db_user

def update_usuario(db: Session, user_id: int, user_update: UsuarioUpdate) -> Optional[models.Usuario]:
    """Atualiza o nome e/ou email de um usuário."""
    db_user = get_usuario(db, user_id)
    if not db_user:
        return None
    
    if user_update.email:
        existing_user_with_email = get_usuario_by_email(db, email=user_update.email)
        if existing_user_with_email and existing_user_with_email.id != user_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já está em uso por outro usuário.")
        db_user.email = user_update.email
    
    if user_update.nome:
        db_user.nome = user_update.nome

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_usuario(db: Session, user_id: int) -> Optional[models.Usuario]:
    """Deleta um usuário do banco de dados."""
    db_user = get_usuario(db, user_id)
    if not db_user:
        return None
        
    db.delete(db_user)
    db.commit()
    return db_user