from pydantic import BaseModel, Field
from uuid import UUID


class InstitutoCreate(BaseModel):
    nome: str = Field(..., max_length=255, example="Instituto de Tecnologia")
    sigla: str = Field(..., max_length=10, example="ITEC")
    universidade_id: UUID

class InstitutoResponse(InstitutoCreate):
    id: UUID

