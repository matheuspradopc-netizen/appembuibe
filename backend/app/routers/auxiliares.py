"""
Router de Endpoints Auxiliares - Expresso Embuibe
Gerencia endpoints auxiliares: cidades, locais de embarque e motoristas
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
from typing import List
from ..database import get_db
from ..models.cidade import Cidade
from ..models.local_embarque import LocalEmbarque
from ..models.motorista import Motorista
from ..models.proprietario import Proprietario
from ..models.usuario import Usuario
from ..utils.security import get_current_user

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class CidadeResponse(BaseModel):
    """Schema de resposta de cidade"""
    id: int
    nome: str
    ordem: int

    class Config:
        from_attributes = True


class LocalEmbarqueResponse(BaseModel):
    """Schema de resposta de local de embarque"""
    id: int
    nome: str
    valor: Decimal
    ativo: bool

    class Config:
        from_attributes = True


class ProprietarioSimples(BaseModel):
    """Schema simplificado de proprietário"""
    id: int
    nome: str

    class Config:
        from_attributes = True


class MotoristaResponse(BaseModel):
    """Schema de resposta de motorista"""
    id: int
    nome: str
    vagas: int
    ativo: bool
    proprietario: ProprietarioSimples

    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINTS - CIDADES
# ============================================================================

@router.get("/cidades", response_model=List[CidadeResponse])
def listar_cidades(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todas as cidades ordenadas pela ordem definida

    Args:
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Lista de cidades ordenadas
    """
    cidades = db.query(Cidade).order_by(Cidade.ordem).all()
    return [CidadeResponse.model_validate(c) for c in cidades]


@router.get("/cidades/{cidade_id}/locais", response_model=List[LocalEmbarqueResponse])
def listar_locais_por_cidade(
    cidade_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todos os locais de embarque de uma cidade específica

    Retorna apenas locais ativos, ordenados por nome.

    Args:
        cidade_id: ID da cidade
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Lista de locais de embarque da cidade

    Raises:
        HTTPException 404: Se a cidade não for encontrada
    """
    # Verifica se a cidade existe
    cidade = db.query(Cidade).filter(Cidade.id == cidade_id).first()
    if not cidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cidade não encontrada"
        )

    # Busca locais ativos da cidade
    locais = db.query(LocalEmbarque).filter(
        LocalEmbarque.cidade_id == cidade_id,
        LocalEmbarque.ativo == True
    ).order_by(LocalEmbarque.nome).all()

    return [LocalEmbarqueResponse.model_validate(l) for l in locais]


# ============================================================================
# ENDPOINTS - MOTORISTAS
# ============================================================================

@router.get("/motoristas", response_model=List[MotoristaResponse])
def listar_motoristas(
    apenas_ativos: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todos os motoristas com seus proprietários

    Args:
        apenas_ativos: Se True, retorna apenas motoristas ativos (padrão: True)
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Lista de motoristas com dados do proprietário
    """
    query = db.query(Motorista)

    if apenas_ativos:
        query = query.filter(Motorista.ativo == True)

    motoristas = query.order_by(Motorista.nome).all()

    # Monta resposta com dados do proprietário
    resultado = []
    for motorista in motoristas:
        proprietario = db.query(Proprietario).filter(
            Proprietario.id == motorista.proprietario_id
        ).first()

        resultado.append(MotoristaResponse(
            id=motorista.id,
            nome=motorista.nome,
            vagas=motorista.vagas,
            ativo=motorista.ativo,
            proprietario=ProprietarioSimples(
                id=proprietario.id,
                nome=proprietario.nome
            )
        ))

    return resultado


@router.get("/motoristas/{motorista_id}", response_model=MotoristaResponse)
def buscar_motorista(
    motorista_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Busca um motorista específico por ID

    Args:
        motorista_id: ID do motorista
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Dados do motorista com proprietário

    Raises:
        HTTPException 404: Se o motorista não for encontrado
    """
    motorista = db.query(Motorista).filter(Motorista.id == motorista_id).first()

    if not motorista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motorista não encontrado"
        )

    proprietario = db.query(Proprietario).filter(
        Proprietario.id == motorista.proprietario_id
    ).first()

    return MotoristaResponse(
        id=motorista.id,
        nome=motorista.nome,
        vagas=motorista.vagas,
        ativo=motorista.ativo,
        proprietario=ProprietarioSimples(
            id=proprietario.id,
            nome=proprietario.nome
        )
    )


# ============================================================================
# ENDPOINTS - LOCAIS DE EMBARQUE (GERAL)
# ============================================================================

@router.get("/locais-embarque", response_model=List[dict])
def listar_todos_locais(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todos os locais de embarque agrupados por cidade

    Retorna apenas locais ativos, agrupados e ordenados.

    Args:
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Lista de cidades com seus locais de embarque
    """
    cidades = db.query(Cidade).order_by(Cidade.ordem).all()

    resultado = []
    for cidade in cidades:
        locais = db.query(LocalEmbarque).filter(
            LocalEmbarque.cidade_id == cidade.id,
            LocalEmbarque.ativo == True
        ).order_by(LocalEmbarque.nome).all()

        if locais:  # Só adiciona cidades que têm locais
            resultado.append({
                "cidade": {
                    "id": cidade.id,
                    "nome": cidade.nome,
                    "ordem": cidade.ordem
                },
                "locais": [
                    {
                        "id": local.id,
                        "nome": local.nome,
                        "valor": float(local.valor)
                    }
                    for local in locais
                ]
            })

    return resultado
