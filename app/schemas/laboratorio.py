from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from uuid import UUID

from app.schemas.equipe import EquipeResponse 

class LaboratorioRegistroCreate(BaseModel):
    nome: str = Field(..., max_length=255, examples=["Laboratório de Inteligência Artificial"])
    sigla: str = Field(..., max_length=10, examples=["LIA"])
    unidade_academica_id: UUID
    descricao: Optional[str] = Field(None, description="Descrição em formato longo")
    areas_linhas_pesquisa: Optional[str] = Field(None)
    servicos_disponiveis: Optional[str] = Field(None)
    equipamentos: Optional[str] = Field(None)
    site: Optional[str] = Field(None, max_length=500)
    email: Optional[EmailStr] = Field(None)
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = Field(None, max_length=255)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=50)
    cep: Optional[str] = Field(None, max_length=10)
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)
    email_institucional: EmailStr = Field(..., examples=["docente@ufpa.br"])

class LaboratorioResponse(BaseModel):
    id: UUID
    unidade_academica_id: UUID
    nome: str
    sigla: str
    imagens: List[str] = []
    descricao: Optional[str]
    areas_linhas_pesquisa: Optional[str]
    servicos_disponiveis: Optional[str]
    equipamentos: Optional[str]
    site: Optional[str]
    email: Optional[str]
    telefone: Optional[str]
    endereco: Optional[str]
    cidade: Optional[str]
    estado: Optional[str]
    cep: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    aprovado: bool
    membros_equipe: List[EquipeResponse] = []

    class Config:
        from_attributes = True

class LaboratorioUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    imagens: Optional[List[str]] = Field(None) 
    descricao: Optional[str] = Field(None)
    areas_linhas_pesquisa: Optional[str] = Field(None)
    servicos_disponiveis: Optional[str] = Field(None)
    equipamentos: Optional[str] = Field(None)
    site: Optional[str] = Field(None, max_length=500)
    email: Optional[EmailStr] = Field(None)
    telefone: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)