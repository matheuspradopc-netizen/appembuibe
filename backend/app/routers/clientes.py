"""
Router de Clientes - Expresso Embuibe
Gerencia endpoints CRUD de clientes/passageiros
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import math
from ..database import get_db
from ..models.cliente import Cliente
from ..models.usuario import Usuario
from ..schemas.cliente import (
    ClienteCreate,
    ClienteUpdate,
    ClienteResponse,
    ClienteListItem,
    ClientePaginatedResponse
)
from ..utils.security import get_current_user

router = APIRouter()


@router.get("", response_model=ClientePaginatedResponse)
def listar_clientes(
    q: Optional[str] = Query(None, description="Busca por nome ou telefone"),
    page: int = Query(1, ge=1, description="Página atual"),
    limit: int = Query(20, ge=1, le=50000, description="Itens por página"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista clientes com busca e paginação

    Permite buscar por nome ou telefone parcial.
    Retorna apenas clientes ativos.

    Args:
        q: Termo de busca (opcional)
        page: Número da página
        limit: Itens por página
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Lista paginada de clientes
    """
    # Query base
    query = db.query(Cliente).filter(Cliente.ativo == True)

    # Aplica filtro de busca se fornecido
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Cliente.nome.ilike(search_term),
                Cliente.telefone.ilike(search_term)
            )
        )

    # Conta total de resultados
    total = query.count()

    # Calcula total de páginas
    total_pages = math.ceil(total / limit)

    # Aplica paginação e ordenação alfabética (A-Z, caracteres especiais por último)
    # COLLATE NOCASE garante ordenação case-insensitive
    offset = (page - 1) * limit
    clientes = query.order_by(Cliente.nome.collate('NOCASE')).offset(offset).limit(limit).all()

    return ClientePaginatedResponse(
        items=[ClienteListItem.model_validate(c) for c in clientes],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/{cliente_id}", response_model=ClienteResponse)
def buscar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Busca um cliente por ID

    Args:
        cliente_id: ID do cliente
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Dados completos do cliente

    Raises:
        HTTPException 404: Se o cliente não for encontrado
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    return ClienteResponse.model_validate(cliente)


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    cliente_data: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria um novo cliente

    Args:
        cliente_data: Dados do cliente
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Cliente criado

    Raises:
        HTTPException 400: Se já existir cliente com mesmo telefone
    """
    # Verifica se já existe cliente com o mesmo telefone
    existing = db.query(Cliente).filter(
        Cliente.telefone == cliente_data.telefone,
        Cliente.ativo == True
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um cliente cadastrado com o telefone {cliente_data.telefone}"
        )

    # Cria o novo cliente
    cliente = Cliente(**cliente_data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return ClienteResponse.model_validate(cliente)


@router.put("/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(
    cliente_id: int,
    cliente_data: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza um cliente existente

    Args:
        cliente_id: ID do cliente
        cliente_data: Dados a serem atualizados
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Cliente atualizado

    Raises:
        HTTPException 404: Se o cliente não for encontrado
        HTTPException 400: Se o telefone já estiver em uso por outro cliente
    """
    # Busca o cliente
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    # Se está atualizando o telefone, verifica se já existe
    if cliente_data.telefone and cliente_data.telefone != cliente.telefone:
        existing = db.query(Cliente).filter(
            Cliente.telefone == cliente_data.telefone,
            Cliente.ativo == True,
            Cliente.id != cliente_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe outro cliente cadastrado com o telefone {cliente_data.telefone}"
            )

    # Atualiza os campos fornecidos
    update_data = cliente_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cliente, field, value)

    db.commit()
    db.refresh(cliente)

    return ClienteResponse.model_validate(cliente)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Desativa um cliente (soft delete)

    Não remove o cliente do banco, apenas marca como inativo.

    Args:
        cliente_id: ID do cliente
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Raises:
        HTTPException 404: Se o cliente não for encontrado
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    cliente.ativo = False
    db.commit()

    return None
