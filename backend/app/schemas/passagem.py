"""
Schemas Pydantic de Passagens - Expresso Embuibe
Define os schemas de validação para passagens
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, time
from decimal import Decimal


class PassagemBase(BaseModel):
    """Schema base de passagem"""
    cliente_id: int = Field(..., description="ID do cliente/passageiro")
    local_embarque_id: int = Field(..., description="ID do local de embarque")
    motorista_id: int = Field(..., description="ID do motorista")
    horario: time = Field(..., description="Horário da viagem (HH:MM)")
    data_viagem: date = Field(..., description="Data da viagem (YYYY-MM-DD)")
    forma_pagamento: str = Field(..., description="Forma de pagamento: DINHEIRO, CARTAO ou PIX")
    endereco_embarque: Optional[str] = Field(None, description="Endereço onde a van vai buscar o passageiro")


class PassagemCreate(PassagemBase):
    """Schema para criação de passagem"""
    pass


class PassagemResponse(PassagemBase):
    """Schema de resposta de passagem"""
    id: int
    numero: int
    valor: Decimal
    status: str
    data_emissao: datetime
    atendente_id: int
    created_at: datetime
    endereco_embarque: Optional[str] = None

    class Config:
        from_attributes = True


class PassagemDetalhada(BaseModel):
    """Schema detalhado de passagem com dados relacionados"""
    id: int
    numero: int
    data_viagem: date
    horario: time
    valor: Decimal
    forma_pagamento: str
    status: str
    data_emissao: datetime

    # Dados do cliente
    cliente_nome: str
    cliente_telefone: str

    # Dados do local
    cidade: str
    local_embarque: str
    endereco_embarque: Optional[str] = None  # Endereço específico de busca

    # Dados do motorista
    motorista_nome: str
    proprietario_nome: str

    # Dados do atendente
    atendente_nome: str
    
    # Dados de alteração (cancelamento/transferência)
    data_original: Optional[date] = None
    horario_original: Optional[time] = None
    motivo_alteracao: Optional[str] = None

    class Config:
        from_attributes = True


class PassagemEmitidaResponse(BaseModel):
    """Schema de resposta após emissão de passagem"""
    passagem: PassagemResponse
    pdf_base64: str = Field(..., description="PDF da passagem em base64")


class PassagemListItem(BaseModel):
    """Schema simplificado para listagem de passagens"""
    id: int
    numero: int
    cliente_nome: str
    data_viagem: date
    horario: time
    valor: Decimal
    status: str

    class Config:
        from_attributes = True


# ==================== CANCELAMENTO E TRANSFERÊNCIA ====================

class PassagemCancelar(BaseModel):
    """Schema para cancelamento de passagem"""
    motivo: Optional[str] = Field(None, description="Motivo do cancelamento")


class PassagemTransferir(BaseModel):
    """Schema para transferência de passagem"""
    nova_data: date = Field(..., description="Nova data da viagem")
    novo_horario: time = Field(..., description="Novo horário da viagem")
    novo_motorista_id: int = Field(..., description="ID do novo motorista")
    motivo: Optional[str] = Field(None, description="Motivo da transferência")


class PassagemAlteradaResponse(BaseModel):
    """Schema de resposta após alteração (cancelamento/transferência)"""
    id: int
    numero: int
    status: str
    data_viagem: date
    horario: time
    data_original: Optional[date]
    horario_original: Optional[time]
    motivo_alteracao: Optional[str]
    mensagem: str

    class Config:
        from_attributes = True
