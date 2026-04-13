from fastapi import APIRouter, HTTPException, Depends, status,  Request, Response, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from datetime import timedelta
from onelogin.saml2.auth import OneLogin_Saml2_Auth
import os

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

def prepare_saml_auth(request: Request):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    base_dir = os.path.dirname(current_dir)
    saml_path = os.path.join(base_dir, "saml")
    
    if not os.path.exists(saml_path):
        raise Exception(f"Pasta SAML não encontrada no caminho: {saml_path}")

    req = {
        "http_host": request.url.hostname,
        "script_name": request.url.path,
        "server_port": request.url.port or (443 if request.url.scheme == "https" else 80),
        "get_data": request.query_params._dict,
        "post_data": {},
        "https": "on" if request.url.scheme == "https" else "off"
    }
    
    return OneLogin_Saml2_Auth(req, custom_base_path=saml_path)


@router.get("/metadata", summary="Gerar Metadados SAML para o IdP")
async def saml_metadata(request: Request):
    """
    Esta rota não tem tela. Ela apenas gera e retorna um arquivo XML.
    O IdP (UFPA) precisa acessar esta URL para registrar o seu sistema.
    """
    try:
        auth = prepare_saml_auth(request)
        settings = auth.get_settings()
        
        # A biblioteca gera o XML inteiro automaticamente baseado no seu JSON!
        metadata = settings.get_sp_metadata()
        
        # Valida se você não esqueceu nada no JSON
        errors = settings.validate_metadata(metadata)
        
        if len(errors) == 0:
            return Response(content=metadata, media_type="application/xml")
        else:
            return Response(
                content=f"Erro na configuração do SAML: {', '.join(errors)}", 
                status_code=500
            )
    except Exception as e:
        return Response(content=f"Erro fatal ao gerar metadados: {str(e)}", status_code=500)
    

@router.get("/login", summary="Redirecionar para o Login da UFPA")
async def saml_login(request: Request):
    """
    O botão 'Entrar com UFPA' do frontend deve apontar para cá.
    """
    auth = prepare_saml_auth(request)
    
    # Gera o URL de redirecionamento para o IdP da UFPA
    url_redirecionamento = auth.login()
    
    # Envia o utilizador para lá
    return RedirectResponse(url=url_redirecionamento)

@router.post("/acs", summary="Receber os dados do IdP da UFPA")
async def saml_acs(
    request: Request, 
    session: Session = Depends(get_session)
):
    """
    Esta rota é chamada EXCLUSIVAMENTE pelo servidor da UFPA após o utilizador logar lá.
    O Frontend não chama isto diretamente.
    """
    # 1. Extrair os dados do formulário POST que a UFPA enviou
    form_data = await request.form()
    post_data_dict = {k: v for k, v in form_data.items()}
    
    # 2. Precisamos de recriar o objeto de requisição incluindo os dados POST
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    saml_path = os.path.join(base_dir, "saml")
    
    req = {
        "http_host": request.url.hostname,
        "script_name": request.url.path,
        "server_port": request.url.port or (443 if request.url.scheme == "https" else 80),
        "get_data": request.query_params._dict,
        "post_data": post_data_dict, # <-- Agora injetamos o XML recebido aqui!
        "https": "on" if request.url.scheme == "https" else "off"
    }
    
    auth = OneLogin_Saml2_Auth(req, custom_base_path=saml_path)
    
    # 3. Processar e validar a assinatura da UFPA
    auth.process_response()
    erros = auth.get_errors()
    
    if erros:
        motivo = auth.get_last_error_reason()
        print(f"Erro SAML: {erros} - {motivo}")
        return RedirectResponse(url="https://O_SEU_FRONTEND.com/erro?msg=falha_saml")

    if auth.is_authenticated():
        # 4. Sucesso! Extrair os atributos (E-mail, Nome, CPF)
        atributos = auth.get_attributes()
        
        # NOTA: Os nomes 'mail', 'cn' e 'brPersonCPF' são o padrão do Shibboleth. 
        # O Gabriel pode usar nomes ligeiramente diferentes. Se falhar, faça print(atributos) para ver as chaves.
        email = atributos.get('mail', [''])[0]
        nome = atributos.get('cn', ['Usuario UFPA'])[0]
        cpf = atributos.get('brPersonCPF', [None])[0]
        
        # 5. REGRA DE NEGÓCIO: Apenas @ufpa.br (Bloquear alunos)
        if not email.endswith("@ufpa.br"):
            return RedirectResponse(url="https://O_SEU_FRONTEND.com/erro?msg=acesso_apenas_servidores")
            
        # 6. AUTO-PROVISIONAMENTO: O utilizador já existe na nossa base de dados?
        statement = select(Usuario).where(Usuario.email == email)
        usuario = session.exec(statement).first()
        
        if not usuario:
            # É a primeira vez deste professor! Vamos criar a conta dele automaticamente.
            usuario = Usuario(
                login=email.split('@')[0], # ex: usa 'thiago' do 'thiago@ufpa.br'
                nome=nome,
                email=email,
                cpf=cpf,
                senha="LOGIN_VIA_CAFE", # Senha simbólica, ele nunca a vai usar
                tipo="SERVIDOR" 
            )
            session.add(usuario)
            session.commit()
            session.refresh(usuario)
            
        # 7. GERAR O TOKEN JWT (Usando as suas funções já existentes)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
        access_token = create_access_token(
            data={"sub": usuario.login}, 
            expires_delta=access_token_expires
        )
        
        # 8. DEVOLVER AO FRONTEND: Redirecionar com o token no URL
        # O Frontend deve ter uma rota invisível '/login-sucesso' que apanha este token e guarda no LocalStorage
        url_frontend = f"https://O_SEU_FRONTEND.com/login-sucesso?token={access_token}"
        
        # O status 303 (See Other) é obrigatório após um POST para redirecionar corretamente
        return RedirectResponse(url=url_frontend, status_code=303)
        
    else:
        return RedirectResponse(url="https://O_SEU_FRONTEND.com/erro?msg=nao_autenticado")