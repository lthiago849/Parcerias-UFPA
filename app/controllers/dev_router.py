import pandas as pd
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException

from app.db.db import get_session , async_engine
from app.models.universidade import Universidade
from app.models.unidades_academicas import UnidadesAcademicas
from app.models.usuario import Usuario
from app.const.enums import tipo_usuario

async def criar_entidades():
    """Lê os CSVs e popula o banco de dados em background."""
    
    async with AsyncSession(async_engine) as db_bg:
        try:
            df_univ = pd.read_csv('app/statics/universidades.csv')
            df_inst = pd.read_csv('app/statics/unidade_academica.csv')

            mapa_univ = {}

            #  PROCESSAR UNIVERSIDADES
            for index, row in df_univ.iterrows():
                stmt = select(Universidade).where(Universidade.sigla == row['sigla_universidade'])
                resultado = await db_bg.exec(stmt)
                univ_existente = resultado.first()

                if not univ_existente:
                    nova_univ = Universidade(
                        nome=row['nome_universidade'],
                        sigla=row['sigla_universidade'],
                        campus=row['campus_universidade']
                    )
                    db_bg.add(nova_univ)
                    await db_bg.flush() 
                    mapa_univ[nova_univ.sigla] = nova_univ.id
                else:
                    mapa_univ[univ_existente.sigla] = univ_existente.id

            # PROCESSAR UNIDADES_ACADEMICAS
            for index, row in df_inst.iterrows():
                sigla_univ = row['sigla_universidade']
                
                # Pega o ID da universidade que guardámos no passo anterior
                univ_id = mapa_univ.get(sigla_univ)

                if not univ_id:
                    print(f"⚠️ Aviso: Universidade {sigla_univ} não encontrada para o instituto {row['sigla_unidade_academica']}")
                    continue 

                # Verifica se o instituto já existe
                stmt_inst = select(UnidadesAcademicas).where(UnidadesAcademicas.sigla == row['sigla_unidade_academica'])
                resultado_inst = await db_bg.exec(stmt_inst)
                inst_existente = resultado_inst.first()

                if not inst_existente:
                    novo_inst = UnidadesAcademicas(
                        nome=row['nome_unidade_academica'],
                        sigla=row['sigla_unidade_academica'],
                        universidade_id=univ_id # Faz a ligação perfeita aqui!
                    )
                    db_bg.add(novo_inst)

            await db_bg.commit()
            print("Criação de universidades e institutos concluída com sucesso!")

        except Exception as e:
            await db_bg.rollback()
            print(f"❌ Erro ao popular entidades: {e}")

async def alterar_tipo_usuario(
    usuario_id: UUID, 
    novo_tipo: tipo_usuario, 
    db: AsyncSession
):
    query = select(Usuario).where(Usuario.id == usuario_id)
    result = await db.exec(query)
    usuario = result.first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    usuario.tipo = novo_tipo

    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)

    return usuario