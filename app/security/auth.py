import bcrypt


from uuid import UUID
from datetime import datetime, timedelta, timezone

from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.schemas.auth import TokenData, UsuarioOut
from app.models.usuario import Usuario
from app.db.db import get_session
from app.const.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRES_MINUTES


CREDENTIAL_EXCEPTION = HTTPException(
    status_code=401,
    detail="Não pôde validar as credenciais",
    headers={"WWW-Authenticate": "Bearer"}
)
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/usuario/token")

def get_hash(plain: str) -> str:
    """Retorna o hash de uma string <plain>"""
    password_bytes = plain.encode('utf-8')
    
    salt = bcrypt.gensalt()
    
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    
    return hashed_bytes.decode('utf-8')
def verify_password(plain_text: str, hash_text: str) -> bool:
    """Compara o hash plain com o hash do banco de dados"""
    plain_text_bytes = plain_text.encode('utf-8')
    hash_text_bytes = hash_text.encode('utf-8')
    
    try:
        return bcrypt.checkpw(plain_text_bytes, hash_text_bytes)
    except ValueError:
        return False


async def get_user(username: str, session: Session) -> UsuarioOut:
    """Decode an OAuth access <token> and return the User"""
    statement = select(Usuario).where(Usuario.login == username)
    result = await session.exec(statement)
    user = result.one_or_none()
    if not user:
        await session.close()
        raise CREDENTIAL_EXCEPTION

    return user


async def authenticate_user(username: str, plain: str, session: Session):
    """Authenticate user <name> and <plain> password"""
    user = await get_user(username, session)
    password = verify_password(plain, user.senha)
    if not user:
        return False

    if not password:
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRES_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(session: Session = Depends(get_session),
                           token: str = Depends(oauth_scheme)) -> UsuarioOut:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
        raise CREDENTIAL_EXCEPTION

    token_data = TokenData(username=username)
    result = await get_user(username=token_data.username, session=session)
    if result is None:
        raise CREDENTIAL_EXCEPTION

    user = UsuarioOut(
        id=result.id,
        login=result.login,
        email=result.email,
        tipo=result.tipo,
        nome=result.nome)
    return user


async def get_current_id(session: Session = Depends(get_session),
                         token: str = Depends(oauth_scheme)) -> UUID:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
        raise CREDENTIAL_EXCEPTION

    token_data = TokenData(username=username)
    result = await get_user(username=token_data.username, session=session)
    if result is None:
        raise CREDENTIAL_EXCEPTION

    return result.id
