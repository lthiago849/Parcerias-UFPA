from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.db import get_session
from app.security.auth import get_current_user
from app.schemas.auth import UsuarioOut 
from app.schemas.email_log import EmailCreate 

from app.controllers.email import enviar_email_interesse_background

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