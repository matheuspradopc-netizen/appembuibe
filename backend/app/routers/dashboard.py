"""
Router de Dashboard - Expresso Embuibe
Gerencia endpoints de métricas e resumos para dashboard
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import date, datetime, timedelta, time
from decimal import Decimal
from typing import List, Optional
from ..database import get_db
from ..models.passagem import Passagem
from ..models.viagem import Viagem
from ..models.motorista import Motorista
from ..models.proprietario import Proprietario
from ..models.usuario import Usuario
from ..utils.security import get_current_user

router = APIRouter()


class MetricasPeriodo(BaseModel):
    """Schema de métricas de um período"""
    passageiros: int
    valor: Decimal
    viagens: int


class UltimaViagemDashboard(BaseModel):
    """Schema de última viagem no dashboard"""
    horario: time
    motorista: str
    proprietario: str
    passageiros: int
    valor: Decimal


class TopMotorista(BaseModel):
    """Schema de top motorista"""
    motorista: str
    proprietario: str
    total_passageiros: int
    total_viagens: int
    valor_total: Decimal


class ResumoFormaPagamento(BaseModel):
    """Schema de resumo por forma de pagamento"""
    forma: str
    total: int
    valor: Decimal
    percentual: float


class DashboardResumo(BaseModel):
    """Schema do resumo do dashboard"""
    hoje: MetricasPeriodo
    semana: MetricasPeriodo
    mes: MetricasPeriodo
    ultimas_viagens: List[UltimaViagemDashboard]
    top_motoristas_mes: List[TopMotorista]
    formas_pagamento_hoje: List[ResumoFormaPagamento]


@router.get("/resumo", response_model=DashboardResumo)
def dashboard_resumo(
    data: Optional[date] = Query(None, description="Data de referência (opcional, padrão: hoje)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna resumo completo para o dashboard

    Calcula métricas de hoje, semana e mês, além de listar
    as últimas viagens e top motoristas.

    Args:
        data: Data de referência (opcional, padrão: hoje)
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Resumo completo do dashboard
    """
    # Data de referência
    if data is None:
        data_ref = datetime.now().date()
    else:
        data_ref = data

    # Calcula datas dos períodos
    inicio_semana = data_ref - timedelta(days=data_ref.weekday())  # Segunda-feira
    inicio_mes = data_ref.replace(day=1)

    # Métricas de HOJE
    passagens_hoje = db.query(Passagem).filter(
        Passagem.data_viagem == data_ref,
        Passagem.status != "CANCELADA"
    ).all()

    viagens_hoje = db.query(Viagem).filter(
        Viagem.data == data_ref
    ).count()

    metricas_hoje = MetricasPeriodo(
        passageiros=len(passagens_hoje),
        valor=sum(p.valor for p in passagens_hoje) if passagens_hoje else Decimal('0'),
        viagens=viagens_hoje
    )

    # Métricas da SEMANA
    passagens_semana = db.query(Passagem).filter(
        Passagem.data_viagem >= inicio_semana,
        Passagem.data_viagem <= data_ref,
        Passagem.status != "CANCELADA"
    ).all()

    viagens_semana = db.query(Viagem).filter(
        Viagem.data >= inicio_semana,
        Viagem.data <= data_ref
    ).count()

    metricas_semana = MetricasPeriodo(
        passageiros=len(passagens_semana),
        valor=sum(p.valor for p in passagens_semana) if passagens_semana else Decimal('0'),
        viagens=viagens_semana
    )

    # Métricas do MÊS
    passagens_mes = db.query(Passagem).filter(
        Passagem.data_viagem >= inicio_mes,
        Passagem.data_viagem <= data_ref,
        Passagem.status != "CANCELADA"
    ).all()

    viagens_mes = db.query(Viagem).filter(
        Viagem.data >= inicio_mes,
        Viagem.data <= data_ref
    ).count()

    metricas_mes = MetricasPeriodo(
        passageiros=len(passagens_mes),
        valor=sum(p.valor for p in passagens_mes) if passagens_mes else Decimal('0'),
        viagens=viagens_mes
    )

    # Últimas 5 viagens registradas
    ultimas_viagens_db = db.query(Viagem).order_by(
        Viagem.data.desc(),
        Viagem.horario.desc()
    ).limit(5).all()

    ultimas_viagens = []
    for viagem in ultimas_viagens_db:
        motorista = db.query(Motorista).filter(Motorista.id == viagem.motorista_id).first()
        proprietario = db.query(Proprietario).filter(
            Proprietario.id == motorista.proprietario_id
        ).first()

        ultimas_viagens.append(UltimaViagemDashboard(
            horario=viagem.horario,
            motorista=motorista.nome,
            proprietario=proprietario.nome,
            passageiros=viagem.total_passageiros,
            valor=viagem.valor_total
        ))

    # Top 5 motoristas do mês
    from collections import defaultdict
    motoristas_stats = defaultdict(lambda: {
        'total_passageiros': 0,
        'total_viagens': 0,
        'valor_total': Decimal('0'),
        'proprietario': ''
    })

    viagens_mes_db = db.query(Viagem).filter(
        Viagem.data >= inicio_mes,
        Viagem.data <= data_ref
    ).all()

    for viagem in viagens_mes_db:
        motorista = db.query(Motorista).filter(Motorista.id == viagem.motorista_id).first()
        proprietario = db.query(Proprietario).filter(
            Proprietario.id == motorista.proprietario_id
        ).first()

        motoristas_stats[motorista.nome]['total_passageiros'] += viagem.total_passageiros
        motoristas_stats[motorista.nome]['total_viagens'] += 1
        motoristas_stats[motorista.nome]['valor_total'] += viagem.valor_total
        motoristas_stats[motorista.nome]['proprietario'] = proprietario.nome

    # Ordena por total de passageiros e pega top 5
    top_motoristas = sorted(
        motoristas_stats.items(),
        key=lambda x: x[1]['total_passageiros'],
        reverse=True
    )[:5]

    top_motoristas_list = [
        TopMotorista(
            motorista=nome,
            proprietario=stats['proprietario'],
            total_passageiros=stats['total_passageiros'],
            total_viagens=stats['total_viagens'],
            valor_total=stats['valor_total']
        )
        for nome, stats in top_motoristas
    ]

    # Resumo por forma de pagamento (hoje)
    formas_stats = defaultdict(lambda: {'total': 0, 'valor': Decimal('0')})

    for passagem in passagens_hoje:
        formas_stats[passagem.forma_pagamento]['total'] += 1
        formas_stats[passagem.forma_pagamento]['valor'] += passagem.valor

    total_passagens_hoje = len(passagens_hoje)
    formas_pagamento = []

    for forma, stats in formas_stats.items():
        percentual = (stats['total'] / total_passagens_hoje * 100) if total_passagens_hoje > 0 else 0
        formas_pagamento.append(ResumoFormaPagamento(
            forma=forma,
            total=stats['total'],
            valor=stats['valor'],
            percentual=round(percentual, 2)
        ))

    # Ordena por total
    formas_pagamento.sort(key=lambda x: x.total, reverse=True)

    return DashboardResumo(
        hoje=metricas_hoje,
        semana=metricas_semana,
        mes=metricas_mes,
        ultimas_viagens=ultimas_viagens,
        top_motoristas_mes=top_motoristas_list,
        formas_pagamento_hoje=formas_pagamento
    )


@router.get("/metricas-rapidas")
def metricas_rapidas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna métricas rápidas para atualização em tempo real

    Args:
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Métricas básicas do dia
    """
    hoje = datetime.now().date()

    # Passagens do dia
    passagens_hoje = db.query(Passagem).filter(
        Passagem.data_viagem == hoje,
        Passagem.status != "CANCELADA"
    ).count()

    # Viagens registradas hoje
    viagens_hoje = db.query(Viagem).filter(
        Viagem.data == hoje
    ).count()

    # Valor total do dia
    passagens = db.query(Passagem).filter(
        Passagem.data_viagem == hoje,
        Passagem.status != "CANCELADA"
    ).all()

    valor_total = sum(p.valor for p in passagens) if passagens else Decimal('0')

    return {
        "passagens": passagens_hoje,
        "viagens": viagens_hoje,
        "valor_total": float(valor_total),
        "data": hoje.isoformat()
    }
