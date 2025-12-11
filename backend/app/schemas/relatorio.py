"""
Schemas Pydantic de Relatórios - Expresso Embuibe
Define os schemas de validação para relatórios
"""
from pydantic import BaseModel, Field
from datetime import date, time
from decimal import Decimal
from typing import List


class PassageiroRelatorio(BaseModel):
    """Schema de passageiro no relatório"""
    nome: str
    local_embarque: str
    valor: Decimal


class ViagemRelatorio(BaseModel):
    """Schema de viagem no relatório"""
    motorista: str
    proprietario: str
    passageiros: int
    valor_total: Decimal
    passageiros_lista: List[PassageiroRelatorio] = []


class HorarioRelatorio(BaseModel):
    """Schema de horário no relatório"""
    horario: str
    viagens: List[ViagemRelatorio]
    total_passageiros: int
    valor_total: Decimal


class RelatorioDiario(BaseModel):
    """Schema do relatório diário"""
    data: date
    horarios: List[HorarioRelatorio]
    total_passageiros: int
    valor_total: Decimal
    total_viagens: int


class PassagemPeriodo(BaseModel):
    """Schema de passagem no relatório por período"""
    numero: int
    data_viagem: date
    horario: time
    cliente_nome: str
    motorista_nome: str
    proprietario_nome: str
    local_embarque: str
    cidade: str
    valor: Decimal
    forma_pagamento: str


class RelatorioPeriodo(BaseModel):
    """Schema do relatório por período"""
    data_inicio: date
    data_fim: date
    passagens: List[PassagemPeriodo]
    total_passagens: int
    total_passageiros: int
    valor_total: Decimal
    resumo_por_motorista: List['ResumoMotorista']
    resumo_por_forma_pagamento: List['ResumoFormaPagamento']


class ResumoMotorista(BaseModel):
    """Schema de resumo por motorista"""
    motorista_nome: str
    proprietario_nome: str
    total_passagens: int
    valor_total: Decimal


class ResumoFormaPagamento(BaseModel):
    """Schema de resumo por forma de pagamento"""
    forma_pagamento: str
    total_passagens: int
    valor_total: Decimal


class ViagemMotorista(BaseModel):
    """Schema de viagem no relatório por motorista"""
    data: date
    horario: time
    total_passageiros: int
    valor_total: Decimal
    passageiros: List[PassageiroRelatorio]


class RelatorioMotorista(BaseModel):
    """Schema do relatório por motorista"""
    motorista_nome: str
    proprietario_nome: str
    data_inicio: date
    data_fim: date
    viagens: List[ViagemMotorista]
    total_viagens: int
    total_passageiros: int
    valor_total: Decimal


# Rebuild models to resolve forward references
RelatorioPeriodo.model_rebuild()
