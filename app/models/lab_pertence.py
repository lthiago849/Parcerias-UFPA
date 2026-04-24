from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

class LabPertence(SQLModel, table=True):
    __tablename__ = "lab_pertence"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    usuario_id: UUID = Field(foreign_key="usuario.id", nullable=False)
    laboratorio_id: UUID = Field(foreign_key="laboratorio.id", nullable=False)