from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, TEXT, JSON
from uuid import UUID, uuid4
from datetime import datetime, date
from typing import Optional, List
from app.utils.validacoes import validar_horario
from app.models.lab_pertence import LabPertence

class Laboratorio(SQLModel, table=True):
    __tablename__ = "laboratorio"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    unidade_academica_id: UUID = Field(foreign_key="unidades_academicas.id", nullable=False)
    nome: str = Field(max_length=255, nullable=False)
    sigla: str = Field(max_length=10, unique=True, nullable=False)
    imagens: Optional[list[str]] = Field(default=[], sa_column=Column(JSON))
    descricao: Optional[str] = Field(default=None, sa_column=Column(TEXT)) 
    areas_linhas_pesquisa: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    servicos_disponiveis: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    equipamentos: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    site: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=500)
    telefone: Optional[str] = Field(default=None, max_length=20)
    endereco: Optional[str] = Field(default=None, max_length=255)
    cidade: Optional[str] = Field(default=None, max_length=100)
    estado: Optional[str] = Field(default=None, max_length=50)
    cep: Optional[str] = Field(default=None, max_length=10)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    atualizado_em: datetime = Field(default_factory=validar_horario, nullable=False, sa_column_kwargs={"onupdate": validar_horario})
    atualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuario.id")
    aprovado: bool = Field(default=False, nullable=False)
    publicado_em: Optional[date] = Field(default_factory=date.today)

    unidade_academica: Optional["UnidadesAcademicas"] = Relationship(back_populates="laboratorios")
    membros_equipe: List["Equipe"] = Relationship(
    back_populates="laboratorio",
    sa_relationship_kwargs={"lazy": "selectin"}
)
    usuarios: list["Usuario"] = Relationship(
        back_populates="laboratorios", 
        link_model=LabPertence
    )