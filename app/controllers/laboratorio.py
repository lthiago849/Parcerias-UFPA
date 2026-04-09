
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID
import logging
from sqlmodel import select


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
        dados_dict = dados.model_dump()
        
        novo_lab = Laboratorio(
            **dados_dict,
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
    

async def get_laboratorios(db: AsyncSession):

    query = (select(Laboratorio)
    )


    result = await db.exec(query)
    linhas = result.all()

    laboratorios_formatados = []
    

    for lab in linhas:
        laboratorios_formatados.append({
            "id": lab.id,
            "nome": lab.nome,
            "sigla": lab.sigla,
            "unidade_academica_id": lab.unidade_academica_id,
            "aprovado": lab.aprovado        })

    return laboratorios_formatados


async def get_equipe_laboratorio(
    db: AsyncSession,
    laboratorio_id : UUID
):
    query = select(Equipe).where(Equipe.laboratorio_id == laboratorio_id).order_by(Equipe.nome)
    result = await db.exec(query)
    equipe = result.all()

    equipe_laboratorio_formatado = []

    for integrante in equipe:
        equipe_laboratorio_formatado.append({
            "id": integrante.id,
            "nome": integrante.nome,
            "funcao": integrante.funcao,
            "email": integrante.email,
            "lattes": integrante.lattes
        })

    return equipe_laboratorio_formatado 