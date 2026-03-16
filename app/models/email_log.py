from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text
from datetime import datetime
from app.utils.validacoes import validar_horario

class EmailLog(SQLModel, table=True):
    __tablename__ = "email_log"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    interesse_id: UUID = Field(foreign_key="interesse.id", nullable=False)
    remetente: str = Field(max_length=255, nullable=False)
    destinatario: str = Field(max_length=255, nullable=False)
    assunto: str = Field(max_length=255, nullable=False)
    corpo: str = Field(sa_column=Column(Text, nullable=False))
    enviado_em: datetime = Field(default_factory=validar_horario, nullable=False)