from pydantic import BaseModel
from uuid import UUID
from app.const.enums import tipo_interesse

class InteresseCreate(BaseModel):
    usuario_id: UUID
    propriedade_intelectual_id: UUID
    tipo: tipo_interesse

class InteresseResponse(InteresseCreate):
    id: UUID