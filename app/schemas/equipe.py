from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

from app.const.enums import tipo_funcao

class EquipeCreate(BaseModel):
    nome: str = Field(..., max_length=255, examples=["Maria Souza"])
    laboratorio_id: UUID 
    funcao: tipo_funcao = Field(..., examples=[tipo_funcao.PESQUISADOR_PESQUISADORA])
    email: Optional[EmailStr] = Field(None, examples=["maria.souza@ufpa.br"])
    lattes: Optional[str] = Field(None, max_length=50, examples=["http://lattes.cnpq.br/123456789"])

class EquipeResponse(BaseModel):
    id: UUID
    laboratorio_id: UUID
    nome: Optional[str]
    funcao: Optional[tipo_funcao]
    email: Optional[str]
    lattes: Optional[str]

    class Config:
        from_attributes = True