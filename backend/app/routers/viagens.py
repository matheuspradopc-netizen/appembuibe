"""
Router de Viagens - Expresso Embuibe
Gerencia endpoints de registro de saídas de viagens
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import date, time
from decimal import Decimal
from typing import List
from ..database import get_db
from ..models.viagem import Viagem
from ..models.passagem import Passagem
from ..models.cliente import Cliente
from ..models.local_embarque import LocalEmbarque
from ..models.motorista import Motorista
from ..models.proprietario import Proprietario
from ..models.usuario import Usuario
from ..utils.security import get_current_user

router = APIRouter()


class RegistrarSaidaRequest(BaseModel):
    """Schema para request de registro de saída"""
    data: date = Field(..., description="Data da viagem (YYYY-MM-DD)")
    horario: time = Field(..., description="Horário da viagem (HH:MM)")
    motorista_id: int = Field(..., description="ID do motorista")


class PassageiroManifesto(BaseModel):
    """Schema de passageiro no manifesto"""
    numero_passagem: int
    nome: str
    local_embarque: str
    cidade: str
    valor: Decimal


class ViagemRegistrada(BaseModel):
    """Schema de viagem registrada"""
    id: int
    data: date
    horario: time
    motorista_nome: str
    proprietario_nome: str
    total_passageiros: int
    valor_total: Decimal


class RegistrarSaidaResponse(BaseModel):
    """Schema de resposta do registro de saída"""
    viagem: ViagemRegistrada
    passageiros: List[PassageiroManifesto]


@router.post("/buscar-manifesto", response_model=dict)
def buscar_manifesto(
    dados: RegistrarSaidaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Busca o manifesto de passageiros ANTES de confirmar a saída

    Retorna as passagens emitidas para data/horário/motorista sem registrar a viagem

    Args:
        dados: Dados da viagem (data, horário, motorista)
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Manifesto com passageiros e totais

    Raises:
        HTTPException 404: Se motorista não for encontrado
    """
    # Busca o motorista
    motorista = db.query(Motorista).filter(Motorista.id == dados.motorista_id).first()
    if not motorista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motorista não encontrado"
        )

    # Busca o proprietário do motorista
    from ..models.proprietario import Proprietario
    proprietario = db.query(Proprietario).filter(
        Proprietario.id == motorista.proprietario_id
    ).first()

    # Busca todas as passagens EMITIDAS para esta viagem
    passagens = db.query(Passagem).filter(
        Passagem.data_viagem == dados.data,
        Passagem.horario == dados.horario,
        Passagem.motorista_id == dados.motorista_id,
        Passagem.status == "EMITIDA"
    ).all()

    # Monta lista de passageiros para o manifesto
    passageiros_manifesto = []
    valor_total = Decimal(0)

    for passagem in passagens:
        cliente = db.query(Cliente).filter(Cliente.id == passagem.cliente_id).first()
        local = db.query(LocalEmbarque).filter(
            LocalEmbarque.id == passagem.local_embarque_id
        ).first()

        # Busca a cidade do local
        from ..models.cidade import Cidade
        cidade = db.query(Cidade).filter(Cidade.id == local.cidade_id).first()

        passageiros_manifesto.append({
            "numero_passagem": passagem.numero,
            "nome": cliente.nome if cliente else "Desconhecido",
            "cliente_nome": cliente.nome if cliente else "Desconhecido",
            "cliente_telefone": cliente.telefone if cliente and cliente.telefone else "N/A",
            "local_embarque": local.nome if local else "N/A",
            "cidade": cidade.nome if cidade else "N/A",
            "valor": float(passagem.valor) if passagem.valor else 0.0,
            "forma_pagamento": passagem.forma_pagamento or "N/A"
        })

        valor_total += passagem.valor or 0

    # Ordena passageiros por nome
    passageiros_manifesto.sort(key=lambda p: p["cliente_nome"])

    return {
        "total_passageiros": len(passageiros_manifesto),
        "valor_total": float(valor_total),
        "motorista_nome": motorista.nome,
        "proprietario_nome": proprietario.nome if proprietario else "N/A",
        "passageiros": passageiros_manifesto
    }


@router.post("/registrar-saida", response_model=RegistrarSaidaResponse, status_code=status.HTTP_201_CREATED)
def registrar_saida(
    dados: RegistrarSaidaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registra a saída de uma viagem

    Busca todas as passagens do dia/horário/motorista, calcula totais
    e cria o registro da viagem. Retorna o manifesto de passageiros.

    Args:
        dados: Dados da viagem (data, horário, motorista)
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Viagem registrada com lista de passageiros

    Raises:
        HTTPException 404: Se motorista não for encontrado
        HTTPException 400: Se não houver passagens para a viagem
    """
    # Busca o motorista
    motorista = db.query(Motorista).filter(Motorista.id == dados.motorista_id).first()
    if not motorista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motorista não encontrado"
        )

    # Busca o proprietário
    proprietario = db.query(Proprietario).filter(
        Proprietario.id == motorista.proprietario_id
    ).first()

    # Busca todas as passagens da viagem
    passagens = db.query(Passagem).filter(
        Passagem.data_viagem == dados.data,
        Passagem.horario == dados.horario,
        Passagem.motorista_id == dados.motorista_id,
        Passagem.status == "EMITIDA"
    ).all()

    if not passagens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não há passagens emitidas para {motorista.nome} no dia {dados.data} às {dados.horario}"
        )

    # Calcula totais
    total_passageiros = len(passagens)
    valor_total = sum(p.valor for p in passagens)

    # Verifica se já existe registro para esta viagem
    viagem_existente = db.query(Viagem).filter(
        Viagem.data == dados.data,
        Viagem.horario == dados.horario,
        Viagem.motorista_id == dados.motorista_id
    ).first()

    if viagem_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saída já registrada para esta viagem"
        )

    # Cria o registro da viagem
    viagem = Viagem(
        data=dados.data,
        horario=dados.horario,
        motorista_id=dados.motorista_id,
        total_passageiros=total_passageiros,
        valor_total=valor_total,
        atendente_id=current_user.id
    )

    db.add(viagem)
    db.commit()
    db.refresh(viagem)

    # Atualiza status das passagens para UTILIZADA
    for passagem in passagens:
        passagem.status = "UTILIZADA"
    db.commit()

    # Monta lista de passageiros para o manifesto
    passageiros_manifesto = []
    for passagem in passagens:
        cliente = db.query(Cliente).filter(Cliente.id == passagem.cliente_id).first()
        local = db.query(LocalEmbarque).filter(
            LocalEmbarque.id == passagem.local_embarque_id
        ).first()

        # Busca a cidade do local
        from ..models.cidade import Cidade
        cidade = db.query(Cidade).filter(Cidade.id == local.cidade_id).first()

        passageiros_manifesto.append(PassageiroManifesto(
            numero_passagem=passagem.numero,
            nome=cliente.nome,
            local_embarque=local.nome,
            cidade=cidade.nome,
            valor=passagem.valor
        ))

    # Ordena passageiros por nome
    passageiros_manifesto.sort(key=lambda p: p.nome)

    return RegistrarSaidaResponse(
        viagem=ViagemRegistrada(
            id=viagem.id,
            data=viagem.data,
            horario=viagem.horario,
            motorista_nome=motorista.nome,
            proprietario_nome=proprietario.nome,
            total_passageiros=viagem.total_passageiros,
            valor_total=viagem.valor_total
        ),
        passageiros=passageiros_manifesto
    )


@router.get("/listar", response_model=List[ViagemRegistrada])
def listar_viagens(
    data_inicio: date = None,
    data_fim: date = None,
    motorista_id: int = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista viagens registradas com filtros opcionais

    Args:
        data_inicio: Data inicial (opcional)
        data_fim: Data final (opcional)
        motorista_id: ID do motorista (opcional)
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Lista de viagens registradas
    """
    query = db.query(Viagem)

    # Aplica filtros
    if data_inicio:
        query = query.filter(Viagem.data >= data_inicio)
    if data_fim:
        query = query.filter(Viagem.data <= data_fim)
    if motorista_id:
        query = query.filter(Viagem.motorista_id == motorista_id)

    viagens = query.order_by(Viagem.data.desc(), Viagem.horario.desc()).all()

    # Monta lista de resposta
    resultado = []
    for viagem in viagens:
        motorista = db.query(Motorista).filter(Motorista.id == viagem.motorista_id).first()
        proprietario = db.query(Proprietario).filter(
            Proprietario.id == motorista.proprietario_id
        ).first()

        resultado.append(ViagemRegistrada(
            id=viagem.id,
            data=viagem.data,
            horario=viagem.horario,
            motorista_nome=motorista.nome,
            proprietario_nome=proprietario.nome,
            total_passageiros=viagem.total_passageiros,
            valor_total=viagem.valor_total
        ))

    return resultado


@router.get("/{viagem_id}/manifesto", response_model=List[PassageiroManifesto])
def obter_manifesto(
    viagem_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém o manifesto de passageiros de uma viagem registrada

    Args:
        viagem_id: ID da viagem
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Lista de passageiros da viagem

    Raises:
        HTTPException 404: Se a viagem não for encontrada
    """
    # Busca a viagem
    viagem = db.query(Viagem).filter(Viagem.id == viagem_id).first()
    if not viagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viagem não encontrada"
        )

    # Busca as passagens da viagem
    passagens = db.query(Passagem).filter(
        Passagem.data_viagem == viagem.data,
        Passagem.horario == viagem.horario,
        Passagem.motorista_id == viagem.motorista_id
    ).all()

    # Monta lista de passageiros
    passageiros_manifesto = []
    for passagem in passagens:
        cliente = db.query(Cliente).filter(Cliente.id == passagem.cliente_id).first()
        local = db.query(LocalEmbarque).filter(
            LocalEmbarque.id == passagem.local_embarque_id
        ).first()

        from ..models.cidade import Cidade
        cidade = db.query(Cidade).filter(Cidade.id == local.cidade_id).first()

        passageiros_manifesto.append(PassageiroManifesto(
            numero_passagem=passagem.numero,
            nome=cliente.nome,
            local_embarque=local.nome,
            cidade=cidade.nome,
            valor=passagem.valor
        ))

    # Ordena passageiros por nome
    passageiros_manifesto.sort(key=lambda p: p.nome)

    return passageiros_manifesto


@router.post("/confirmar-saida")
def confirmar_saida(
    dados: RegistrarSaidaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Confirma a saída de uma viagem

    Marca a viagem como "SAIU" e registra data/hora de saída.

    Args:
        dados: Dados da viagem (data, horário, motorista)
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Dados da viagem confirmada

    Raises:
        HTTPException 404: Se viagem não for encontrada
        HTTPException 400: Se viagem já foi confirmada
    """
    from datetime import datetime

    # Busca a viagem
    viagem = db.query(Viagem).filter(
        Viagem.data == dados.data,
        Viagem.horario == dados.horario,
        Viagem.motorista_id == dados.motorista_id
    ).first()

    if not viagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viagem não encontrada. Certifique-se de que há passagens emitidas para esta data/horário/motorista."
        )

    if viagem.status == "SAIU":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta viagem já foi registrada como saída"
        )

    # Marcar como SAIU
    viagem.status = "SAIU"
    viagem.data_saida = datetime.now()

    db.commit()
    db.refresh(viagem)

    # Buscar motorista e proprietário para retorno
    motorista = db.query(Motorista).filter(Motorista.id == viagem.motorista_id).first()
    proprietario = db.query(Proprietario).filter(
        Proprietario.id == motorista.proprietario_id
    ).first()

    return {
        "mensagem": "Saída registrada com sucesso!",
        "viagem": {
            "id": viagem.id,
            "horario": viagem.horario.strftime("%H:%M"),
            "motorista": motorista.nome,
            "proprietario": proprietario.nome,
            "passageiros": viagem.total_passageiros,
            "valor": float(viagem.valor_total),
            "data_saida": viagem.data_saida.isoformat(),
            "status": viagem.status
        }
    }
