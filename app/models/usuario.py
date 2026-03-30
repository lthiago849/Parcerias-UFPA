from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from datetime import datetime
from app.const.enums import tipo_usuario
from app.utils.validacoes import validar_horario
from typing import Optional


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    login: str = Field(max_length=255, nullable=False, unique=True)
    nome: str = Field(max_length=255, nullable=False)
    email: str = Field(max_length=255, nullable=False, unique=True)
    senha: str = Field(min_length=6, nullable=False)
    tipo: tipo_usuario = Field(nullable=False)
    siape: Optional[str] = Field(default=None, max_length=20, unique=True)
    telefone: Optional[str] = Field(default=None, max_length=20)
    cpf: Optional[str] = Field(default=None, max_length=14, unique=True)
    cnpj: Optional[str] = Field(default=None, max_length=18, unique=True)
    endereco: Optional[str] = Field(default=None, max_length=255)
    cidade: Optional[str] = Field(default=None, max_length=100)
    estado: Optional[str] = Field(default=None, max_length=50)
    pais: Optional[str] = Field(default=None, max_length=50)
    cep: Optional[str] = Field(default=None, max_length=10)
    nacionalidade: Optional[str] = Field(default=None, max_length=50)
    instituicao: Optional[str] = Field(default=None, max_length=255)
    criado_em: datetime = Field(default_factory=validar_horario, nullable=False)
    atualizado_em: datetime = Field(default_factory=validar_horario, nullable=False, sa_column_kwargs={"onupdate": validar_horario})