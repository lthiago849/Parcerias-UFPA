from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.const.enums import tipo_registro, categoria_pi

class PropriedadeIntelectualCreate(BaseModel):
    titulo: str = Field(..., max_length=255, example="Novo Motor Elétrico")
    resumo: str = Field(..., example="Este motor é capaz de...")
    imagens: Optional[list[str]] = Field(default=[], example=["uploads/img1.png"])
    tipo: tipo_registro 
    categoria: categoria_pi 
    titulares: str = Field(..., max_length=500, example="UFPA, FADESP")
    inventores: str = Field(..., max_length=1000, example="João Silva, Maria Souza")
    palavras_chave: str = Field(..., max_length=255, example="motor, elétrico, inovação")
    laboratorio_id: UUID

class PropriedadeIntelectualResponse(PropriedadeIntelectualCreate):
    id: UUID
    titulo: str
    criado_em: datetime
    atualizado_em: datetime