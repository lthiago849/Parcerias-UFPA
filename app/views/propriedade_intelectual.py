import os
import shutil
from uuid import uuid4, UUID
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from  sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_session
from app.security.auth import get_current_id

from app.schemas.propriedade_intelectual import PropriedadeIntelectualResponse, PropriedadeIntelectualCreate
from app.utils.validacoes import validar_tipo_usuario
from app.controllers.propriedade_intelectual import criar_propriedade_intelectual


router = APIRouter(prefix="/propriedade", tags=["Propriedade Intelectual"])

# Define a pasta onde as imagens vão ficar guardadas
UPLOAD_DIR = "uploads"
# Cria a pasta automaticamente se ela não existir
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-imagem/")
async def upload_imagem(file: UploadFile = File(...)):
    """Recebe uma imagem, guarda na pasta local e devolve o caminho."""
    
    # Valida se é realmente uma imagem (opcional, mas recomendado)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Ficheiro deve ser uma imagem.")

    # Gera um nome único para não haver conflitos (ex: 8f3a...12.png)
    extensao = file.filename.split(".")[-1]
    novo_nome_ficheiro = f"{uuid4()}.{extensao}"
    caminho_completo = os.path.join(UPLOAD_DIR, novo_nome_ficheiro)

    # Guarda o ficheiro fisicamente na pasta "uploads"
    with open(caminho_completo, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Devolve o caminho para ser usado na criação da propriedade
    return {"caminho_imagem": caminho_completo}

@router.post("/", response_model = PropriedadeIntelectualResponse, status_code = 201)
async def criar_propriedade_intelectual_endpoint(
    dados : PropriedadeIntelectualCreate,
    db: AsyncSession = Depends(get_session),
    usuario_id : UUID = Depends(get_current_id)
):
    await validar_tipo_usuario(usuario_id,db)

    nova_pi = await criar_propriedade_intelectual(db, dados)

    return nova_pi
