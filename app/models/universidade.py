from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from app.models.instituto import Instituto

class Universidade(SQLModel, table=True):
    __tablename__ = "universidade"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    nome: str = Field(max_length=255, unique=True, nullable=False)
    sigla: str = Field(max_length=10, unique=True, nullable=False)
    campus: str = Field(max_length=255, nullable=False)

    institutos: List["Instituto"] = Relationship(back_populates="universidade")