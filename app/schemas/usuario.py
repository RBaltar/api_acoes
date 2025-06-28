from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UsuarioBase(BaseModel):
    email: EmailStr
    nome: str = Field(..., min_length=3, description="Nome do usuário")

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nome: Optional[str] = Field(None, min_length=3, description="Novo nome do usuário")

class UsuarioOut(UsuarioBase):
    id: int
    ativo: bool

    class Config:
        from_attributes = True