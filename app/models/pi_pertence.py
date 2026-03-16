from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class PiPertence(SQLModel, table=True):
    __tablename__ = "pi_pertence"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    propriedade_intelectual_id: UUID = Field(foreign_key="propriedade_intelectual.id", nullable=False)
    laboratorio_id: UUID = Field(foreign_key="laboratorio.id", nullable=False)

