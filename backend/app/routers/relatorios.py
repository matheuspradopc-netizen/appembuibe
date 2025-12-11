"""
Router de Relatórios - Expresso Embuibe
Gerencia endpoints de geração de relatórios
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional
from ..database import get_db
from ..models.usuario import Usuario
from ..schemas.relatorio import (
    RelatorioDiario,
    RelatorioPeriodo,
    RelatorioMotorista
)
from ..services.relatorio_service import relatorio_service
from ..utils.security import get_current_user

router = APIRouter()


@router.get("/diario")
def relatorio_diario(
    data: Optional[date] = Query(None, description="Data do relatório (YYYY-MM-DD). Se não informada, usa hoje"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera relatório diário agrupado por horário

    Mostra todas as passagens do dia organizadas por horário e motorista.
    Inclui totais por horário e totais gerais.

    Args:
        data: Data do relatório (opcional, padrão: hoje)
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Relatório diário estruturado
    """
    # Se data não informada, usa hoje
    if data is None:
        data = datetime.now().date()

    try:
        relatorio = relatorio_service.gerar_relatorio_diario(db, data)
        return relatorio
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )


@router.get("/periodo", response_model=RelatorioPeriodo)
def relatorio_periodo(
    data_inicio: date = Query(..., description="Data inicial (YYYY-MM-DD)"),
    data_fim: date = Query(..., description="Data final (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera relatório por período

    Lista todas as passagens do período com resumos por motorista
    e por forma de pagamento.

    Args:
        data_inicio: Data inicial do período
        data_fim: Data final do período
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Relatório do período com resumos

    Raises:
        HTTPException 400: Se data_inicio > data_fim
    """
    # Valida datas
    if data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data inicial não pode ser maior que data final"
        )

    try:
        relatorio = relatorio_service.gerar_relatorio_periodo(db, data_inicio, data_fim)
        return relatorio
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )


@router.get("/motorista/{motorista_id}", response_model=RelatorioMotorista)
def relatorio_motorista(
    motorista_id: int,
    data_inicio: date = Query(..., description="Data inicial (YYYY-MM-DD)"),
    data_fim: date = Query(..., description="Data final (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera relatório por motorista

    Mostra todas as viagens de um motorista específico no período,
    com lista de passageiros em cada viagem.

    Args:
        motorista_id: ID do motorista
        data_inicio: Data inicial do período
        data_fim: Data final do período
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Relatório do motorista

    Raises:
        HTTPException 400: Se data_inicio > data_fim
        HTTPException 404: Se motorista não for encontrado
    """
    # Valida datas
    if data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data inicial não pode ser maior que data final"
        )

    try:
        relatorio = relatorio_service.gerar_relatorio_motorista(
            db, motorista_id, data_inicio, data_fim
        )
        return relatorio
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )
