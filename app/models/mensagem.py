from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
from datetime import datetime
from typing import Optional
from app.utils.validacoes import validar_horario

class Mensagem(SQLModel, table=True):
    __tablename__ = "mensagem"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    email_id: UUID = Field(foreign_key="email.id", nullable=False) 
    
    remetente: str = Field(max_length=255, nullable=False)
    destinatario: str = Field(max_length=255, nullable=False)
    corpo: str = Field(sa_column=Column(Text, nullable=False))
    enviado_em: datetime = Field(default_factory=validar_horario, nullable=False)

    # Relacionamento de volta para a email
    email: Optional["Email"] = Relationship(back_populates="mensagens")