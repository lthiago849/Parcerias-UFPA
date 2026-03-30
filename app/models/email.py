from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
from datetime import datetime
from typing import Optional, List

from app.utils.validacoes import validar_horario
from app.const.enums import tipo_status_email

class Email(SQLModel, table=True):
    __tablename__ = "email"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True) 
    interesse_id: Optional[UUID] = Field(default=None, foreign_key="interesse.id", nullable=True)    
    assunto_principal: str = Field(max_length=255, nullable=False)
    criado_em: datetime = Field(default_factory=validar_horario, nullable=False)
    status: tipo_status_email = Field(default=tipo_status_email.ATIVO, nullable=False)
    # Relacionamento: Uma conversa tem VÁRIAS mensagens
    mensagens: List["Mensagem"] = Relationship(back_populates="email")