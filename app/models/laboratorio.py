from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class Laboratorio(SQLModel, table=True):
    __tablename__ = "laboratorio"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    nome: str = Field(max_length=255, nullable=False)
    sigla: str = Field(max_length=10, unique=True, nullable=False)
    unidade_academica_id: UUID = Field(foreign_key="unidades_academicas.id", nullable=False)
    aprovado: bool = Field(default=False, nullable=False)

    unidade_academica: Optional["UnidadesAcademicas"] = Relationship(back_populates="laboratorios")