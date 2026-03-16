from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class Laboratorio(SQLModel, table=True):
    __tablename__ = "laboratorio"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    nome: str = Field(max_length=255, nullable=False)
    sigla: str = Field(max_length=10, unique=True, nullable=False)
    instituto_id: UUID = Field(foreign_key="instituto.id", nullable=False)
    aprovado: bool = Field(default=False, nullable=False)

    instituto: Optional["Instituto"] = Relationship(back_populates="laboratorios")