
from  sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_session
from app.security.auth import get_current_id
from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from pydantic import EmailStr
from uuid import UUID, uuid4
from typing import Optional
import os
import cloudinary
import cloudinary.uploader
import aiofiles
from dotenv import load_dotenv
from app.utils.validacoes import validar_tipo_usuario
from app.controllers.laboratorio import (criar_laboratorio_com_equipe,
                                          criar_novo_integrante_equipe,
                                          get_laboratorios,
                                          get_equipe_laboratorio,
                                          trocar_status_laboratorio
                                          )
from app.schemas.laboratorio import LaboratorioRegistroCreate, LaboratorioResponse
from app.schemas.equipe import EquipeResponse, EquipeCreate

load_dotenv()
router = APIRouter(prefix="/laboratorio", tags=["Laboratorio"])

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


@router.post(
    "/", 
    response_model=LaboratorioResponse, 
    status_code=201,
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        # Apenas os campos realmente obrigatórios para criar o Lab
                        "required": ["nome", "sigla", "unidade_academica_id"],
                        "properties": {
                            "nome":                  {"type": "string"},
                            "sigla":                 {"type": "string", "maxLength": 10},
                            "unidade_academica_id":  {"type": "string", "format": "uuid"},
                            "descricao":             {"type": "string"},
                            "areas_linhas_pesquisa": {"type": "string"},
                            "servicos_disponiveis":  {"type": "string"},
                            "equipamentos":          {"type": "string"},
                            "site":                  {"type": "string"},
                            "email":                 {"type": "string", "format": "email"},
                            "telefone":              {"type": "string"},
                            "endereco":              {"type": "string"},
                            "cidade":                {"type": "string"},
                            "estado":                {"type": "string"},
                            "cep":                   {"type": "string"},
                            "latitude":              {"type": "number", "format": "float"},
                            "longitude":             {"type": "number", "format": "float"},
                            "imagens": {
                                "type": "array", 
                                "items": {"type": "string", "format": "binary"}
                            }
                        }
                    }
                }
            }
        }
    }
)
async def registrar_novo_laboratorio(
    nome: str = Form(..., max_length=255),
    sigla: str = Form(..., max_length=10),
    unidade_academica_id: UUID = Form(...),
    descricao: Optional[str] = Form(None),
    areas_linhas_pesquisa: Optional[str] = Form(None),
    servicos_disponiveis: Optional[str] = Form(None),
    equipamentos: Optional[str] = Form(None),
    site: Optional[str] = Form(None, max_length=500),
    email: Optional[str] = Form(None),
    telefone: Optional[str] = Form(None, max_length=20),
    endereco: Optional[str] = Form(None, max_length=255),
    cidade: Optional[str] = Form(None, max_length=100),
    estado: Optional[str] = Form(None, max_length=50),
    cep: Optional[str] = Form(None, max_length=10),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    
    imagens: list[UploadFile] = File(default=[]), 
    
    db: AsyncSession = Depends(get_session),
    usuario_id: UUID = Depends(get_current_id) 
):
    """
    Cria um novo laboratório recebendo dados do formulário e imagens.
    """
    caminhos_imagens = []

    for imagem in imagens:
        if imagem.filename:
            if not imagem.content_type.startswith("image/"):
                raise HTTPException(400, f"O arquivo {imagem.filename} não é uma imagem válida.")

            try:
                conteudo = await imagem.read()
                
                resultado_upload = cloudinary.uploader.upload(
                    conteudo, 
                    folder="parcerias_ufpa/laboratorios",
                    public_id=str(uuid4())
                )
                
                url_segura = resultado_upload.get("secure_url")
                
                caminhos_imagens.append(url_segura)
                
            except Exception as e:
                raise HTTPException(500, f"Erro ao enviar imagem para a nuvem: {str(e)}")
    dados = LaboratorioRegistroCreate(
        nome=nome,
        sigla=sigla,
        unidade_academica_id=unidade_academica_id,
        descricao=descricao,
        areas_linhas_pesquisa=areas_linhas_pesquisa,
        servicos_disponiveis=servicos_disponiveis,
        equipamentos=equipamentos,
        site=site,
        email=email,
        telefone=telefone,
        endereco=endereco,
        cidade=cidade,
        estado=estado,
        cep=cep,
        latitude=latitude,
        longitude=longitude,
        imagens=caminhos_imagens 
    )

    novo_laboratorio = await criar_laboratorio_com_equipe(db, usuario_id, dados)
    return novo_laboratorio

@router.post("/criar-integrante-equipe", response_model= EquipeResponse)
async def registrar_integrante_equipe(
    dados: EquipeCreate,
    db: AsyncSession = Depends(get_session)
):
    integrante_equipe = await criar_novo_integrante_equipe(db, dados)

    return integrante_equipe


@router.get("/get-laboratorios")
async def get_laboratorios_endpoint(
    db: AsyncSession = Depends(get_session),
    aprovado: Optional[bool] = None):

    laboratorios_disponiveis = await get_laboratorios(db, aprovado)

    return laboratorios_disponiveis


@router.get("/get-equipe-laboratorio")
async def get_equipe_laboratorio_endpoint(
    laboratorio_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    equipe = await get_equipe_laboratorio(db, laboratorio_id)

    return equipe

@router.patch("/{laboratorio_id}/trocar-status")
async def trocar_status_laboratorio_endpoint(
    laboratorio_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_id: UUID = Depends(get_current_id)
):
    await validar_tipo_usuario(current_id, db)

    resultado = await trocar_status_laboratorio(laboratorio_id, db)

    return resultado