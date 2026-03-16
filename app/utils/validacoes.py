from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.exceptions.db import instancia_nao_encontrada

def validar_horario() -> datetime:
    hora_atual = datetime.now()
    hora_formatada = hora_atual.replace(microsecond=0)
    return hora_formatada


async def validar_tipo_usuario(_id: UUID, db: AsyncSession):
    from app.models.usuario import Usuario
    usuario = await db.get(Usuario, _id)
    if not usuario:
        instancia_nao_encontrada("usuario")
    if usuario.tipo != "DESENVOLVEDOR":
        raise HTTPException(
            status_code=401, detail="Não autorizado (somente para desenvolvedores)")