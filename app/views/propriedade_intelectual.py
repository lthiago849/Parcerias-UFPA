import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, HTTPException, status

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