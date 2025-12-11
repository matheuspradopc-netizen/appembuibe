"""
Schemas Pydantic de Clientes - Expresso Embuibe
Define os schemas de validação para clientes/passageiros
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ClienteBase(BaseModel):
    """Schema base de cliente"""
    nome: str = Field(..., min_length=3, max_length=200, description="Nome completo do cliente")
    telefone: str = Field(..., min_length=8, max_length=20, description="Telefone para contato")
    cidade: str = Field(..., min_length=2, max_length=100, description="Cidade")
    bairro: Optional[str] = Field(None, max_length=100, description="Bairro")
    endereco: Optional[str] = Field(None, max_length=255, description="Endereço completo")
    cep: Optional[str] = Field(None, max_length=10, description="CEP")


class ClienteCreate(ClienteBase):
    """Schema para criação de cliente"""
    pass


class ClienteUpdate(BaseModel):
    """Schema para atualização de cliente"""
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    telefone: Optional[str] = Field(None, min_length=8, max_length=20)
    endereco: Optional[str] = Field(None, min_length=3, max_length=255)
    bairro: Optional[str] = Field(None, min_length=2, max_length=100)
    cidade: Optional[str] = Field(None, min_length=2, max_length=100)
    cep: Optional[str] = Field(None, min_length=8, max_length=10)
    ativo: Optional[bool] = None


class ClienteResponse(BaseModel):
    """Schema de resposta de cliente"""
    id: int
    nome: str
    telefone: str
    cidade: str
    bairro: Optional[str] = None
    endereco: Optional[str] = None
    cep: Optional[str] = None
    ativo: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClienteListItem(BaseModel):
    """Schema simplificado para listagem de clientes"""
    id: int
    nome: str
    telefone: str
    cidade: str
    bairro: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClientePaginatedResponse(BaseModel):
    """Schema para resposta paginada de clientes"""
    items: list[ClienteListItem]
    total: int
    page: int
    limit: int
    total_pages: int
