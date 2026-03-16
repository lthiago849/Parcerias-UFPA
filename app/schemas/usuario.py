from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.const.enums import tipo_usuario

class UsuarioCreate(BaseModel):
    login: str = Field(..., max_length=255, examples=["joao_silva"])
    nome: str = Field(..., max_length=255, examples=["João da Silva"])
    email: EmailStr = Field(..., examples=["joao.silva@ufpa.br"])
    senha: str = Field(..., min_length=6, examples=["senhaForte123!"])
    tipo: tipo_usuario = Field(..., examples=[tipo_usuario.DOCENTE])

class UsuarioResponse(BaseModel):
    id: UUID
    login: str
    nome: str
    email: EmailStr
    tipo: tipo_usuario
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None)
    senha: Optional[str] = Field(None, min_length=6)
    tipo: Optional[tipo_usuario] = Field(None)