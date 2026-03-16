
from fastapi import APIRouter, Depends
from  sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_session

from app.controllers.entidades import get_universidades, get_institutos, get_laboratorios

router = APIRouter(prefix="/entidade", tags=["Entidade"])

@router.get("/get-universidaes")
async def get_universidades_enpoint(db:AsyncSession = Depends (get_session)):

    universidades_disponiveis = await get_universidades(db)

    return universidades_disponiveis

@router.get("/get-institutos")
async def get_institutos_endpoint(db: AsyncSession = Depends(get_session)):

    institutos_disponiveis = await get_institutos(db)

    return institutos_disponiveis
    

@router.get("/get-laboratorios")
async def get_laboratorios_endpoint(db: AsyncSession = Depends(get_session)):

    laboratorios_disponiveis = await get_laboratorios(db)

    return laboratorios_disponiveis

