from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas import usuario as usuario_schema
from app.services import usuario_service
from app.schemas.msg import Msg

router = APIRouter()

@router.post("/", response_model=usuario_schema.UsuarioOut, status_code=status.HTTP_201_CREATED, summary="Criar um novo Usuário")
def create_user(user: usuario_schema.UsuarioCreate, db: Session = Depends(get_db)):
    # A autenticação não foi adicionada aqui para permitir a criação do primeiro usuário
    # Em um sistema real, esta rota poderia ser protegida ou pública.
    return usuario_service.create_usuario(db=db, user=user)

@router.get("/", response_model=List[usuario_schema.UsuarioOut], summary="Listar todos os Usuários")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return usuario_service.get_usuarios(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=usuario_schema.UsuarioOut, summary="Buscar um Usuário por ID")
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = usuario_service.get_usuario(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user

@router.put("/{user_id}", response_model=usuario_schema.UsuarioOut, summary="Atualizar um Usuário")
def update_user(user_id: int, user: usuario_schema.UsuarioUpdate, db: Session = Depends(get_db)):
    db_user = usuario_service.update_usuario(db=db, user_id=user_id, user_update=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user

@router.delete("/{user_id}", response_model=Msg, summary="Deletar um Usuário")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = usuario_service.delete_usuario(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"detail": f"Usuário {user_id} deletado com sucesso."}