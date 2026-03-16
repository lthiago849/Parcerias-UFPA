from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from app.const.enums import tipo_interesse


class Interesse(SQLModel, table=True):
    __tablename__ = "interesse"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    usuario_id: UUID = Field(foreign_key="usuario.id", nullable=False)
    propriedade_intelectual_id: UUID = Field(foreign_key="propriedade_intelectual.id", nullable=False)
    tipo: tipo_interesse = Field(nullable=False)
    