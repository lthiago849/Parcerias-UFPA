import os
import shutil
from uuid import uuid4, UUID
from fastapi import APIRouter,Depends, UploadFile, File, HTTPException, status,BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_session
from app.security.auth import get_current_id
from app.utils.validacoes import validar_tipo_usuario, validar_tipo_usuario_dev
from app.controllers.dev_router import (
    criar_entidades,
    alterar_tipo_usuario
)
from app.schemas.usuario import TrocarTipoRequest

router = APIRouter(prefix="/dev", tags=["Dev"])

@router.post("/criar-entidades")
async def criar_entidades_endpoint(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session),
    currente_id: UUID = Depends(get_current_id)
):
    await validar_tipo_usuario(currente_id, db)

    background_tasks.add_task(criar_entidades)

    return {"msg": "Processo de criação de entidades iniciado em background"}


@router.patch("/{usuario_id}/trocar-tipo", summary="Altera o nível de acesso (tipo) de um usuário")
async def trocar_tipo_usuario_endpoint(
    usuario_id: UUID,
    dados: TrocarTipoRequest,
    db: AsyncSession = Depends(get_session),
    current_id: UUID = Depends(get_current_id) 
):

    await validar_tipo_usuario_dev(current_id, db)

    usuario_atualizado = await alterar_tipo_usuario(usuario_id, dados.novo_tipo, db)

    return {
        "mensagem": "Tipo de usuário alterado com sucesso.",
        "usuario_id": usuario_atualizado.id,
        "novo_tipo": usuario_atualizado.tipo
    }