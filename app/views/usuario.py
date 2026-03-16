from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta

from app.schemas.auth import UsuarioIn, Token, UsuarioOut
from app.db.db import get_session
from app.security.auth import (
    get_hash,
    authenticate_user,
    create_access_token,
    get_current_user
)
from app.models.usuario import Usuario
from app.const.config import ACCESS_TOKEN_EXPIRES_MINUTES

router = APIRouter(prefix = "/usuario", tags = {"Usuario"})

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(
    user: UsuarioIn,
    session: Session = Depends(get_session)
):
    user.senha = get_hash(user.senha)
    db_user = Usuario(
        login = user.login,
        nome = user.nome,
        email = user.email,
        senha = user.senha,
        tipo = user.tipo
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    await session.close()
    return {"usuario" : db_user}

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UsuarioOut)
async def usuario_logado(
    usuario_atual: UsuarioOut = Depends(get_current_user)
):
    """Retorna os dados do usuário atualmente logado no sistema."""
    return usuario_atual