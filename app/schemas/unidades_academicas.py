from pydantic import BaseModel, Field
from uuid import UUID


class UnidadeAcademicaCreate(BaseModel):
    nome: str = Field(..., max_length=255, example="Unidade Academica de Tecnologia")
    sigla: str = Field(..., max_length=10, example="ITEC")
    universidade_id: UUID

class UnidadeAcademicaResponse(UnidadeAcademicaCreate):
    id: UUID

