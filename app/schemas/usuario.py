from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

# Lembre-se de importar o seu enum atualizado
from app.const.enums import tipo_usuario 

class UsuarioCreate(BaseModel):
    login: str = Field(..., max_length=255, examples=["joao_silva"])
    nome: str = Field(..., max_length=255, examples=["João da Silva"])
    email: EmailStr = Field(..., examples=["joao.silva@ufpa.br"])
    senha: str = Field(..., min_length=6, examples=["senhaForte123!"])
    tipo: tipo_usuario = Field(..., examples=[tipo_usuario.DOCENTE])
    siape: Optional[str] = Field(None, max_length=20)
    telefone: Optional[str] = Field(None, max_length=20, examples=["(91) 98888-7777"])
    cpf: Optional[str] = Field(None, max_length=14, examples=["123.456.789-00"])
    cnpj: Optional[str] = Field(None, max_length=18)
    endereco: Optional[str] = Field(None, max_length=255)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=50)
    pais: Optional[str] = Field(None, max_length=100)
    cep: Optional[str] = Field(None, max_length=10)
    nacionalidade: Optional[str] = Field(None, max_length=100)
    instituicao: Optional[str] = Field(None, max_length=255)

class UsuarioResponse(BaseModel):
    id: UUID
    login: str
    nome: str
    email: EmailStr
    tipo: tipo_usuario
    siape: Optional[str]
    telefone: Optional[str]
    cpf: Optional[str]
    cnpj: Optional[str]
    endereco: Optional[str]
    cidade: Optional[str]
    estado: Optional[str]
    pais: Optional[str]
    cep: Optional[str]
    nacionalidade: Optional[str]
    instituicao: Optional[str]
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None)
    senha: Optional[str] = Field(None, min_length=6)
    tipo: Optional[tipo_usuario] = Field(None)
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = Field(None, max_length=255)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=50)
    cep: Optional[str] = Field(None, max_length=10)
    instituicao: Optional[str] = Field(None, max_length=255)