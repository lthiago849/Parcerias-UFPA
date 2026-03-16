from pydantic import BaseModel, Field
from uuid import UUID

class UniversidadeCreate(BaseModel):
    nome: str = Field(..., max_length=255, example="Universidade Federal do Pará")
    sigla: str = Field(..., max_length=10, example="UFPA")
    campus: str = Field(..., max_length=255, example="Guamá")

class UniversidadeResponse(UniversidadeCreate):
    id: UUID

