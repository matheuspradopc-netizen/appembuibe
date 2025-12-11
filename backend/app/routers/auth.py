"""
Router de Autenticação - Expresso Embuibe
Gerencia endpoints de login e autenticação
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.usuario import LoginRequest, LoginResponse, UsuarioPublic
from ..utils.security import authenticate_user, create_access_token, get_current_user
from ..models.usuario import Usuario

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login

    Autentica um usuário e retorna um token JWT de acesso.

    Args:
        credentials: Login e senha do usuário
        db: Sessão do banco de dados

    Returns:
        Token JWT e dados do usuário

    Raises:
        HTTPException 401: Se as credenciais forem inválidas
    """
    # Autentica o usuário
    user = authenticate_user(db, credentials.login, credentials.senha)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Cria o token JWT
    access_token = create_access_token(data={"sub": str(user.id)})

    # Retorna o token e os dados do usuário
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        usuario=UsuarioPublic(
            id=user.id,
            nome=user.nome,
            tipo=user.tipo
        )
    )


@router.get("/me", response_model=UsuarioPublic)
def get_me(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Endpoint para obter dados do usuário logado

    Requer autenticação via token JWT.

    Args:
        current_user: Usuário atual autenticado (injetado automaticamente)

    Returns:
        Dados públicos do usuário logado
    """
    return UsuarioPublic(
        id=current_user.id,
        nome=current_user.nome,
        tipo=current_user.tipo
    )


@router.post("/logout")
def logout():
    """
    Endpoint de logout

    Como estamos usando JWT stateless, o logout é feito no frontend
    descartando o token. Este endpoint existe apenas para manter
    a consistência da API.

    Returns:
        Mensagem de sucesso
    """
    return {"message": "Logout realizado com sucesso"}
