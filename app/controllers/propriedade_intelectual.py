
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID
import logging

from app.models.propriedade_intelectual import PropriedadeIntelectual
from app.models.pi_pertence import PiPertence
from app.schemas.propriedade_intelectual import PropriedadeIntelectualCreate

logger = logging.getLogger(__name__)

async def criar_propriedade_intelectual(
    db: AsyncSession,
    dados: PropriedadeIntelectualCreate
):
    try:
        nova_pi = PropriedadeIntelectual(
            titulo = dados.titulo,
            resumo = dados.resumo,
            tipo = dados.tipo,
            imagens = dados.imagens,
            categoria = dados.categoria,
            titulares = dados.titulares,
            inventores = dados.inventores,
            palavras_chave = dados.palavras_chave,

        )
        db.add(nova_pi)
        await db.flush()

        novo_vinculo = PiPertence(
            propriedade_intelectual_id = nova_pi.id,
            laboratorio_id = dados.laboratorio_id

        )
        db.add(novo_vinculo)

        await db.commit()
        await db.refresh(nova_pi)

        return {
            "id": nova_pi.id,
            "titulo": nova_pi.titulo,
            "resumo": nova_pi.resumo,
            "imagens": nova_pi.imagens,
            "tipo": nova_pi.tipo,
            "categoria": nova_pi.categoria,
            "titulares": nova_pi.titulares,
            "inventores": nova_pi.inventores,
            "palavras_chave": nova_pi.palavras_chave,
            "criado_em": nova_pi.criado_em,
            "atualizado_em": nova_pi.atualizado_em,
            "laboratorio_id": novo_vinculo.laboratorio_id 
        }
        
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Erro: Já existe uma Propriedade Intelectual registada com este título ou o laboratório indicado não existe."
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))