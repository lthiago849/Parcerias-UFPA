from fastapi import APIRouter, Depends, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.db.db import get_session
from app.models.interesse import Interesse
from app.models.usuario import Usuario
from app.schemas.interesse import InteresseCreate, InteresseResponse
from app.const.enums import tipo_usuario
from app.utils.email import enviar_email_interesse_background

router = APIRouter(prefix="/interesse", tags=["Interesses e Negociações"])

@router.post("/", response_model=InteresseResponse, status_code=201)
async def manifestar_interesse(
    interesse_in: InteresseCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    novo_interesse = Interesse(**interesse_in.model_dump())
    session.add(novo_interesse)
    await session.commit()
    await session.refresh(novo_interesse)

    stmt = select(Usuario).where(Usuario.tipo == tipo_usuario.DESENVOLVEDOR)
    resultado = await session.exec(stmt)
    dev_sistema = resultado.first()

    if dev_sistema:
        # AQUI ESTÁ A MÁGICA: O TICKET NO ASSUNTO PARA O ROBÔ LER DEPOIS!
        assunto = f"Novo Interesse Registado numa PI! [TICKET:{novo_interesse.id}]"
        corpo = f"""
        Olá Desenvolvedor,
        
        Um novo interesse do tipo {novo_interesse.tipo} foi registado.
        ID da Propriedade Intelectual: {novo_interesse.propriedade_intelectual_id}
        ID do Interessado: {novo_interesse.usuario_id}
        
        Por favor, verifique o painel administrativo.
        """
        
        background_tasks.add_task(
            enviar_email_interesse_background,
            session=session,
            interesse_id=novo_interesse.id,
            remetente="sistema-parcerias@ufpa.br", # Como string!
            destinatario=dev_sistema.email,        # Como string!
            assunto=assunto,
            corpo=corpo
        )

    return novo_interesse