from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.universidade import Universidade
from app.models.unidades_academicas import UnidadesAcademicas
from app.models.laboratorio import Laboratorio
from app.models.lab_pertence import LabPertence
from app.models.usuario import Usuario
from sqlmodel.ext.asyncio.session import AsyncSession

async def get_universidades(db: AsyncSession):

    query = select(Universidade)
    result = await db.exec(query)

    universidades= result.all()

    return universidades

async def get_unidades_academicas(db: AsyncSession):

    query = select(UnidadesAcademicas)
    result = await db.exec(query)

    unidades_academicas = result.all()

    return unidades_academicas


async def get_laboratorios(db: AsyncSession):
    query = (
        select(Laboratorio, LabPertence.siape, Usuario.nome)
        .join(LabPertence, Laboratorio.id == LabPertence.laboratorio_id)
        .join(Usuario, LabPertence.usuario_id == Usuario.id)
    )
    
    result = await db.exec(query)
    linhas = result.all()

    laboratorios_formatados = []
    

    for lab, siape, nome_usuario in linhas:
        laboratorios_formatados.append({
            "id": lab.id,
            "nome": lab.nome,
            "sigla": lab.sigla,
            "unidade_academica_id": lab.unidade_academica_id,
            "aprovado": lab.aprovado,
            "siape_responsavel": siape,
            "nome_responsavel": nome_usuario 
        })

    return laboratorios_formatados