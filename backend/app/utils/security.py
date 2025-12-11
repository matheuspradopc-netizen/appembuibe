"""
Funções de Segurança - Expresso Embuibe
Gerencia hash de senhas e JWT tokens
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..models.usuario import Usuario

# Configuração do bearer token
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash

    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash da senha armazenado no banco

    Returns:
        True se a senha estiver correta, False caso contrário
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """
    Gera o hash de uma senha

    Args:
        password: Senha em texto plano

    Returns:
        Hash da senha
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um JWT token de acesso

    Args:
        data: Dados a serem codificados no token
        expires_delta: Tempo de expiração do token (opcional)

    Returns:
        Token JWT assinado
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verifica e decodifica um JWT token

    Args:
        token: Token JWT a ser verificado

    Returns:
        Payload do token decodificado

    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"[DEBUG] Token decodificado com sucesso: {payload}")
        return payload
    except JWTError as e:
        print(f"[DEBUG] Erro ao decodificar token: {e}")
        print(f"[DEBUG] SECRET_KEY: {settings.SECRET_KEY}")
        print(f"[DEBUG] ALGORITHM: {settings.ALGORITHM}")
        raise credentials_exception


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependência que retorna o usuário atual autenticado

    Args:
        credentials: Credenciais HTTP Bearer
        db: Sessão do banco de dados

    Returns:
        Usuário autenticado

    Raises:
        HTTPException: Se o token for inválido ou o usuário não existir
    """
    token = credentials.credentials
    payload = verify_token(token)

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    user_id = int(user_id_str)

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
        )

    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )

    return user


def get_current_admin_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Dependência que verifica se o usuário atual é admin

    Args:
        current_user: Usuário atual autenticado

    Returns:
        Usuário admin autenticado

    Raises:
        HTTPException: Se o usuário não for admin
    """
    if current_user.tipo != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para administradores",
        )

    return current_user


def authenticate_user(db: Session, login: str, password: str) -> Optional[Usuario]:
    """
    Autentica um usuário verificando login e senha

    Args:
        db: Sessão do banco de dados
        login: Login do usuário
        password: Senha em texto plano

    Returns:
        Usuário se autenticado com sucesso, None caso contrário
    """
    user = db.query(Usuario).filter(Usuario.login == login).first()

    if not user:
        return None

    if not verify_password(password, user.senha_hash):
        return None

    if not user.ativo:
        return None

    return user
