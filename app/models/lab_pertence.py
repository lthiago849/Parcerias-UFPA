from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class LabPertence(SQLModel, table=True):
    __tablename__ = "lab_pertence"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    usuario_id: UUID = Field(foreign_key="usuario.id", nullable=False)
    laboratorio_id: UUID = Field(foreign_key="laboratorio.id", nullable=False)
    siape: int = Field(unique=True, nullable=False)
    email_institucional: str = Field(max_length=255, unique=True, nullable=False)
    cpf: str = Field(max_length=40, unique=True, nullable=False)
