
from uuid import  UUID
from fastapi import APIRouter, Depends
from  sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_session
from app.security.auth import get_current_id

from app.controllers.laboratorio import (criar_laboratorio_com_equipe,
                                          criar_novo_integrante_equipe
                                          )
from app.schemas.laboratorio import LaboratorioRegistroCreate, LaboratorioResponse
from app.schemas.equipe import EquipeResponse, EquipeCreate

router = APIRouter(prefix="/laboratorio", tags=["Laboratorio"])


@router.post("/", response_model=LaboratorioResponse, status_code=201)
async def registrar_novo_laboratorio(
    dados: LaboratorioRegistroCreate,
    db: AsyncSession = Depends(get_session),
    usuario_id: UUID = Depends(get_current_id) 
):
    """
    Cria um novo laboratório e automaticamente vincula o docente criador a ele.
    """
    novo_laboratorio = await criar_laboratorio_com_equipe(db, usuario_id, dados)
    return novo_laboratorio

@router.post("/criar-integrante-equipe", response_model= EquipeResponse)
async def registrar_integrante_equipe(
    dados: EquipeCreate,
    db: AsyncSession = Depends(get_session)
):
    integrante_equipe = await criar_novo_integrante_equipe(db, dados)

    return integrante_equipe