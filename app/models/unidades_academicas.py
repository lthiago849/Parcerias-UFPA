from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class UnidadesAcademicas(SQLModel, table=True):
    __tablename__ = "unidades_academicas"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    nome: str = Field(max_length=255, nullable=False)
    sigla: str = Field(max_length=10, unique=True, nullable=False)
    universidade_id: UUID = Field(foreign_key="universidade.id", nullable=False)

    universidade: Optional["Universidade"] = Relationship(back_populates="unidades_academicas")
    laboratorios: List["Laboratorio"] = Relationship(back_populates="unidade_academica")