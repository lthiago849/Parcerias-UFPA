from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import Optional
from app.const.enums import tipo_funcao


class Equipe(SQLModel, table=True):
    __tablename__ = "equipe"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    laboratorio_id: UUID = Field(foreign_key="laboratorio.id", nullable=False)
    nome: Optional[str] = Field(default=None, max_length=255)
    funcao: Optional[tipo_funcao] = Field(default=None)
    email: Optional[str] = Field(default=None, max_length=500)
    lattes: Optional[str] = Field(default=None, max_length=50)

    # Relacionamento de volta para o laboratório
    laboratorio: Optional["Laboratorio"] = Relationship(back_populates="membros_equipe")