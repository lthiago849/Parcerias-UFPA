from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, Enum as SAEnum, Text, JSON
from typing import Optional

from app.const.enums import tipo_registro, categoria_pi
from app.utils.validacoes import validar_horario

class PropriedadeIntelectual(SQLModel, table=True):
    __tablename__ = "propriedade_intelectual"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    titulo: str = Field(max_length=255, nullable=False)
    resumo: str = Field( nullable=False)
    imagens: Optional[list[str]] = Field(default=[], sa_column=Column(JSON))
    tipo: tipo_registro = Field(nullable=False)
    categoria: categoria_pi = Field( nullable=False)
    titulares: str = Field(max_length=500, nullable=False) 
    inventores: str = Field(max_length=1000, nullable=False) 
    palavras_chave: str = Field(max_length=255, nullable=False) 
    criado_em: datetime = Field(default_factory=validar_horario, nullable=False)
    atualizado_em: datetime = Field(default_factory=validar_horario, nullable=False, sa_column_kwargs={"onupdate": validar_horario})