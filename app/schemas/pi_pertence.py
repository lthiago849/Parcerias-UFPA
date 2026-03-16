from pydantic import BaseModel
from uuid import UUID

class PiPertenceCreate(BaseModel):
    propriedade_intelectual_id: UUID
    laboratorio_id: UUID

class PiPertenceResponse(PiPertenceCreate):
    id: UUID

