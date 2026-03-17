import os
import shutil
from uuid import uuid4, UUID
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_session
from app.security.auth import get_current_id
from app.schemas.propriedade_intelectual import PropriedadeIntelectualResponse, PropriedadeIntelectualCreate
from app.utils.validacoes import validar_tipo_usuario
from app.controllers.propriedade_intelectual import criar_propriedade_intelectual

from app.const.enums import tipo_registro, categoria_pi 

router = APIRouter(prefix="/propriedade", tags=["Propriedade Intelectual"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
@router.post("/", response_model=PropriedadeIntelectualResponse, status_code=201)
async def criar_propriedade_intelectual_endpoint(
    titulo: str = Form(...),
    resumo: str = Form(...),
    tipo: tipo_registro = Form(...),
    categoria: categoria_pi = Form(...),
    titulares: str = Form(...),
    inventores: str = Form(...),
    palavras_chave: str = Form(...),
    laboratorio_id: UUID = Form(...),
    imagens: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    usuario_id: UUID = Depends(get_current_id)
):
    await validar_tipo_usuario(usuario_id, db)

    caminhos_imagens = []
    
    if imagens:
        if imagens.filename:
            if not imagens.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"O ficheiro {imagens.filename} não é uma imagem válida.")

            extensao = imagens.filename.split(".")[-1]
            novo_nome_ficheiro = f"{uuid4()}.{extensao}"
            caminho_completo = os.path.join(UPLOAD_DIR, novo_nome_ficheiro)

            with open(caminho_completo, "wb") as buffer:
                shutil.copyfileobj(imagens.imagens, buffer)

            caminhos_imagens.append(caminho_completo)

    dados = PropriedadeIntelectualCreate(
        titulo=titulo,
        resumo=resumo,
        tipo=tipo,
        categoria=categoria,
        titulares=titulares,
        inventores=inventores,
        palavras_chave=palavras_chave,
        laboratorio_id=laboratorio_id,
        imagens=caminhos_imagens 
    )

    nova_pi = await criar_propriedade_intelectual(db, dados)

    return nova_pi