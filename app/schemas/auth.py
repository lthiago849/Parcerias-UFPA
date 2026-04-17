import re

from uuid import UUID
from typing import Optional
from pydantic import BaseModel, field_validator
from app.const.enums import tipo_usuario


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UsuarioIn(BaseModel):
    login: Optional[str] = None
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    tipo: Optional[tipo_usuario] = None


    class Config:
        from_attributes = True

    @field_validator("senha")
    def validar_senha(cls, senha):
        if senha:
            # Requisitos para a senha
            if len(senha) < 8:
                raise ValueError("A senha deve ter pelo menos 8 caracteres.")
            if not re.search(r"[A-Z]", senha):
                raise ValueError("A senha deve conter pelo menos uma letra maiúscula.")
            if not re.search(r"[a-z]", senha):
                raise ValueError("A senha deve conter pelo menos uma letra minúscula.")
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
                raise ValueError("A senha deve conter pelo menos um caractere especial.")
        return senha

class UsuarioOut(BaseModel):
    id: UUID
    login: Optional[str] = None
    email: Optional[str] = None
    tipo: Optional[tipo_usuario] = None
    nome: Optional[str] = None
    
class TokenInput(BaseModel):
    token: str