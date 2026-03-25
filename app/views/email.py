from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.db import get_session
from app.security.auth import get_current_user, get_current_id
from app.schemas.auth import UsuarioOut 
from app.schemas.email_log import EmailCreate, MensagemCreate
from app.utils.validacoes import validar_tipo_usuario


from app.controllers.email import (
    enviar_email_interesse_background,
    trocar_status_email,
    enviar_mensagem,
    disparar_resposta_ticket_background
)

router = APIRouter(prefix="/email", tags=["E-mails"])


@router.post("/enviar")
async def envio_email(
    dados: EmailCreate,
    db: AsyncSession = Depends(get_session),
    usuario_atual: UsuarioOut = Depends(get_current_user)
):
    """
    Rota para disparar e-mails.
    O remetente é preenchido automaticamente com o e-mail do usuário logado.
    """
    
    await enviar_email_interesse_background(
        session=db,
        remetente=usuario_atual.email, 
        nome_remetente=usuario_atual.nome,
        assunto=dados.assunto,
        corpo=dados.corpo,
        interesse_id=dados.interesse_id
    )
    
    return {
        "mensagem": f"E-mail processado com sucesso."
    }

@router.post("/trocar-status-email")
async def trocar_status_email_endpoint(
    email_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_id: UUID = Depends(get_current_id)
):
    await validar_tipo_usuario(current_id, db)

    email = await trocar_status_email(email_id, db)

    return email



@router.post("/enviar-mensagem")
async def enviar_mensagem_endpoint(
    email_id: UUID,
    dados: MensagemCreate, 
    db: AsyncSession = Depends(get_session),
    usuario_atual = Depends(get_current_user) 
):
    await disparar_resposta_ticket_background(
        session=db,
        email_id=email_id,
        usuario_logado=usuario_atual,
        corpo=dados.corpo
    )

    return {"mensagem": "Sua resposta foi enviada e salva na conversa."}