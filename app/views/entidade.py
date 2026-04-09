
from fastapi import APIRouter, Depends
from  sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_session

from app.controllers.entidades import get_universidades, get_unidades_academicas

router = APIRouter(prefix="/entidade", tags=["Entidade"])

@router.get("/get-universidaes")
async def get_universidades_enpoint(db:AsyncSession = Depends (get_session)):

    universidades_disponiveis = await get_universidades(db)

    return universidades_disponiveis

@router.get("/get-unidades-academicas")
async def get_unidades_academicas_endpoint(db: AsyncSession = Depends(get_session)):

    unidades_academicas_disponiveis = await get_unidades_academicas(db)

    return unidades_academicas_disponiveis
    
