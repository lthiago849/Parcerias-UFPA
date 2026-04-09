from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.universidade import Universidade
from app.models.unidades_academicas import UnidadesAcademicas
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

