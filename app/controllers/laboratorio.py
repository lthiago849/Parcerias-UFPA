
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID
import logging

from app.models.laboratorio import Laboratorio
from app.models.equipe import Equipe
from app.schemas.laboratorio import LaboratorioRegistroCreate
from app.schemas.equipe import EquipeCreate

logger = logging.getLogger(__name__)

async def criar_laboratorio_com_equipe(
    db: AsyncSession,
    usuario_id: UUID,
    dados: LaboratorioRegistroCreate
):
    try:
        novo_lab = Laboratorio(
            **dados,
            atualizado_por=usuario_id
        )
        db.add(novo_lab)
        
        await db.commit()
        await db.refresh(novo_lab)

        return novo_lab

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Erro de Integridade no Banco: {e.orig}")
        raise HTTPException(
            status_code=400, 
            detail="Erro: Esta sigla de laboratório já está registrada no sistema."
        )
    except Exception as e:
        await db.rollback()
        logger.exception("Erro inesperado durante a criação do laboratório")
        raise HTTPException(
            status_code=500, 
            detail="Erro interno no servidor ao tentar criar o laboratório."
        )
    
async def criar_novo_integrante_equipe(
    db: AsyncSession,
    dados: EquipeCreate
):
    try:
        # 1. Extraímos os dados do Pydantic para um dicionário
        dados_dict = dados.model_dump(exclude_unset=True)

        # 2. Instanciamos o modelo corretamente usando o '='
        novo_integrante = Equipe(**dados_dict)
        
        db.add(novo_integrante)

        # 3. Usamos commit para salvar definitivamente no banco 
        # (flush apenas prepara o SQL, mas não finaliza a transação)
        await db.commit()
        await db.refresh(novo_integrante)

        # 4. Retornamos o objeto criado
        return novo_integrante

    except Exception as e:
        # 5. O bloco except é obrigatório quando se abre um try
        await db.rollback()
        logger.exception("Erro inesperado ao criar integrante da equipe")
        raise HTTPException(
            status_code=500, 
            detail="Erro interno no servidor ao tentar registrar o integrante."
        )