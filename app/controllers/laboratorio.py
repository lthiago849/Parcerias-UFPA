
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID
import logging

from app.models.laboratorio import Laboratorio
from app.models.lab_pertence import LabPertence
from app.schemas.laboratorio import LaboratorioRegistroCreate

logger = logging.getLogger(__name__)


async def   criar_laboratorio_com_vinculo(
    db: AsyncSession,
    usuario_id: UUID,
    dados: LaboratorioRegistroCreate
):
    try:
        # 1. Preparamos o Laboratório
        novo_lab = Laboratorio(
            nome=dados.nome,
            sigla=dados.sigla,
            unidade_academica_id = dados.unidade_academica_id
        )
        db.add(novo_lab)
        
        # 2. O Segredo: Fazemos o "flush" para o banco gerar o ID do laboratório agora!
        await db.flush() 

        # 3. Preparamos o Vínculo (LabPertence) usando o ID que acabámos de gerar
        novo_vinculo = LabPertence(
            usuario_id=usuario_id,         # Vem do token de quem está logado
            laboratorio_id=novo_lab.id,    # O ID gerado no passo 2
            siape=dados.siape,
            email_institucional=dados.email_institucional,
            cpf=dados.cpf
        )
        db.add(novo_vinculo)

        # 4. Se chegou até aqui sem erros, salvamos as DUAS TABELAS de uma vez!
        await db.commit()
        await db.refresh(novo_lab)

        return {
            "id": novo_lab.id,
            "nome": novo_lab.nome,
            "sigla": novo_lab.sigla,
            "unidade_academica_id": novo_lab.unidade_academica_id,
            "aprovado": novo_lab.aprovado,
            "siape_responsavel": novo_vinculo.siape 
        }

    except IntegrityError as e:
        # Se der erro de integridade (ex: Sigla, SIAPE ou CPF já cadastrados por outra pessoa)
        # O banco faz o rollback automático e não salva nem o Laboratório nem o Vínculo.
        await db.rollback()
        logger.error(f"Erro de Integridade no Banco: {e.orig}")
        raise HTTPException(
            status_code=400, 
            detail="Erro: Esta sigla de laboratório, SIAPE, e-mail institucional ou CPF já estão registados no sistema."
        )
    except Exception as e:
        await db.rollback()
        logger.exception("Erro inesperado durante a criação do laboratório")
        raise HTTPException(status_code=500, detail=str(e))