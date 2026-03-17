from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

from app.db.db import get_session
from app.utils.email import enviar_email_interesse_background
from app.security.auth import get_current_user # <-- 1. Importamos a função que pega o utilizador logado
from app.schemas.auth import UsuarioOut # Apenas para tipagem

router = APIRouter(prefix="/email", tags=["Testes de E-mail"])

# Schema para receber os dados
class EmailTestCreate(BaseModel):
    # REMOVIDO: remetente: EmailStr (O Frontend já não envia isto!)
    destinatario: EmailStr = "cliente_teste@ufpa.br"
    assunto: str = "Testando o disparo de E-mails [TICKET: Teste01]"
    corpo: str = "Olá! Este é um e-mail de teste vindo do FastAPI."
    interesse_id: Optional[UUID] = None

@router.post("/enviar")
async def testar_envio_email(
    dados: EmailTestCreate,
    db: AsyncSession = Depends(get_session),
    usuario_atual: UsuarioOut = Depends(get_current_user) # <-- 2. A MÁGICA: O FastAPI pega o dono do Token!
):
    """Rota para testar o salvamento (e disparo) de e-mails usando o utilizador logado."""
    
    await enviar_email_interesse_background(
        session=db,
        remetente=usuario_atual.email, # <-- 3. Passamos o e-mail do banco de dados automaticamente!
        destinatario=dados.destinatario,
        assunto=dados.assunto,
        corpo=dados.corpo,
        interesse_id=dados.interesse_id
    )
    
    return {
        "mensagem": f"E-mail processado com sucesso em nome de {usuario_atual.email}! Verifique a tabela email_log."
    }