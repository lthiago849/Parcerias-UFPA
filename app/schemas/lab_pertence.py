from pydantic import BaseModel, Field, EmailStr
from uuid import UUID

class LabPertenceCreate(BaseModel):
    usuario_id: UUID
    laboratorio_id: UUID
    siape: int = Field(..., example=1234567)
    email_institucional: EmailStr = Field(..., example="docente@ufpa.br")
    cpf: str = Field(..., max_length=40, example="123.456.789-00")

class LabPertenceResponse(LabPertenceCreate):
    id: UUID
