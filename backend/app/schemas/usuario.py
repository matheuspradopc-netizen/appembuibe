"""
Schemas Pydantic de Usuários - Expresso Embuibe
Define os schemas de validação para usuários e autenticação
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UsuarioBase(BaseModel):
    """Schema base de usuário"""
    nome: str = Field(..., min_length=3, max_length=100, description="Nome completo do usuário")
    login: str = Field(..., min_length=3, max_length=50, description="Login único do usuário")
    tipo: str = Field(..., description="Tipo do usuário: admin ou atendente")


class UsuarioCreate(UsuarioBase):
    """Schema para criação de usuário"""
    senha: str = Field(..., min_length=4, description="Senha do usuário")


class UsuarioUpdate(BaseModel):
    """Schema para atualização de usuário"""
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    senha: Optional[str] = Field(None, min_length=4)
    tipo: Optional[str] = None
    ativo: Optional[bool] = None


class UsuarioResponse(UsuarioBase):
    """Schema de resposta de usuário"""
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UsuarioPublic(BaseModel):
    """Schema público de usuário (sem dados sensíveis)"""
    id: int
    nome: str
    tipo: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Schema para request de login"""
    login: str = Field(..., description="Login do usuário")
    senha: str = Field(..., description="Senha do usuário")


class LoginResponse(BaseModel):
    """Schema para response de login"""
    access_token: str = Field(..., description="Token JWT de acesso")
    token_type: str = Field(default="bearer", description="Tipo do token")
    usuario: UsuarioPublic = Field(..., description="Dados do usuário logado")


class Token(BaseModel):
    """Schema de token JWT"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema dos dados contidos no token"""
    user_id: Optional[int] = None
