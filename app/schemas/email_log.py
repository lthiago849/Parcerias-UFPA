from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class EmailCreate(BaseModel):
    #destinatario: EmailStr = "cliente_teste@icen.ufpa.br"
    assunto: str = "titulo do  E-mails"
    corpo: str = "Olá! gostaria de conhecer um laboratorio."
    interesse_id: Optional[UUID] = None
