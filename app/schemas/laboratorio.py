from pydantic import BaseModel, Field, EmailStr
from uuid import UUID


class LaboratorioRegistroCreate(BaseModel):
    # --- Dados do Laboratório ---
    nome: str = Field(..., max_length=255, example="Laboratório de Inteligência Artificial")
    sigla: str = Field(..., max_length=10, example="LIA")
    unidade_academica_id: UUID

    # --- Dados do Vínculo do Docente ---
    siape: int = Field(..., example=1234567)
    email_institucional: EmailStr = Field(..., example="docente@ufpa.br")
    cpf: str = Field(..., max_length=40, example="123.456.789-00")

# O que a API devolve depois de criar (já deve ter algo parecido)
class LaboratorioResponse(BaseModel):
    id: UUID
    nome: str
    sigla: str
    unidade_academica_id: UUID
    aprovado: bool
    siape_responsavel: int