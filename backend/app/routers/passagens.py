"""
Router de Passagens - Expresso Embuibe
Gerencia endpoints de emissão e consulta de passagens
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from ..database import get_db
from ..models.passagem import Passagem
from ..models.cliente import Cliente
from ..models.local_embarque import LocalEmbarque
from ..models.motorista import Motorista
from ..models.cidade import Cidade
from ..models.proprietario import Proprietario
from ..models.usuario import Usuario
from ..models.viagem import Viagem
from ..schemas.passagem import (
    PassagemCreate,
    PassagemResponse,
    PassagemEmitidaResponse,
    PassagemDetalhada,
    PassagemListItem,
    PassagemCancelar,
    PassagemTransferir,
    PassagemAlteradaResponse
)
from ..utils.security import get_current_user
from ..services.pdf_service import pdf_service
from ..config import settings
import base64

router = APIRouter()


def _gerar_numero_passagem(db: Session) -> int:
    """
    Gera o próximo número de passagem sequencial

    Args:
        db: Sessão do banco de dados

    Returns:
        Próximo número disponível
    """
    # Busca o maior número de passagem existente
    ultimo_numero = db.query(func.max(Passagem.numero)).scalar()

    if ultimo_numero is None:
        # Se não houver passagens, usa o número inicial configurado
        return settings.NUMERO_PASSAGEM_INICIAL

    return ultimo_numero + 1


def _atualizar_viagem_contadores(db: Session, data: date, horario, motorista_id: int, delta_passageiros: int, delta_valor: float):
    """
    Atualiza os contadores de uma viagem (passageiros e valor)
    
    Args:
        db: Sessão do banco de dados
        data: Data da viagem
        horario: Horário da viagem
        motorista_id: ID do motorista
        delta_passageiros: Quantidade a adicionar/remover (pode ser negativo)
        delta_valor: Valor a adicionar/remover (pode ser negativo)
    """
    viagem = db.query(Viagem).filter(
        Viagem.data == data,
        Viagem.horario == horario,
        Viagem.motorista_id == motorista_id
    ).first()
    
    if viagem:
        viagem.total_passageiros += delta_passageiros
        viagem.valor_total += delta_valor
        
        # Remove viagem se ficou sem passageiros
        if viagem.total_passageiros <= 0:
            db.delete(viagem)


@router.post("", response_model=PassagemEmitidaResponse, status_code=status.HTTP_201_CREATED)
def emitir_passagem(
    passagem_data: PassagemCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Emite uma nova passagem

    Gera número sequencial, calcula o valor e cria o PDF.

    Args:
        passagem_data: Dados da passagem
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Passagem emitida com PDF em base64

    Raises:
        HTTPException 404: Se cliente, local ou motorista não forem encontrados
        HTTPException 400: Se a forma de pagamento for inválida
    """
    # Valida forma de pagamento
    formas_validas = ["DINHEIRO", "CARTAO", "PIX"]
    if passagem_data.forma_pagamento.upper() not in formas_validas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Forma de pagamento inválida. Use: {', '.join(formas_validas)}"
        )

    # Busca o cliente
    cliente = db.query(Cliente).filter(Cliente.id == passagem_data.cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    # Busca o local de embarque
    local = db.query(LocalEmbarque).filter(
        LocalEmbarque.id == passagem_data.local_embarque_id
    ).first()
    if not local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local de embarque não encontrado"
        )

    # Busca a cidade do local
    cidade = db.query(Cidade).filter(Cidade.id == local.cidade_id).first()

    # Busca o motorista
    motorista = db.query(Motorista).filter(
        Motorista.id == passagem_data.motorista_id
    ).first()
    if not motorista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motorista não encontrado"
        )

    # Gera o número da passagem
    numero = _gerar_numero_passagem(db)

    # Define endereço de embarque: usa o passado ou monta do cliente
    endereco_embarque = passagem_data.endereco_embarque
    if not endereco_embarque and cliente.endereco:
        # Monta endereço do cliente como padrão
        partes = [cliente.endereco]
        if cliente.bairro:
            partes.append(cliente.bairro)
        if cliente.cidade:
            partes.append(cliente.cidade)
        endereco_embarque = ", ".join(partes)

    # Cria a passagem
    passagem = Passagem(
        numero=numero,
        cliente_id=passagem_data.cliente_id,
        local_embarque_id=passagem_data.local_embarque_id,
        motorista_id=passagem_data.motorista_id,
        horario=passagem_data.horario,
        data_viagem=passagem_data.data_viagem,
        valor=local.valor,  # Valor vem do local de embarque
        forma_pagamento=passagem_data.forma_pagamento.upper(),
        atendente_id=current_user.id,
        status="EMITIDA",
        endereco_embarque=endereco_embarque
    )

    db.add(passagem)
    db.flush()  # Garante que a passagem está no banco antes de criar/atualizar viagem

    # Atualizar ou criar viagem automaticamente
    viagem = db.query(Viagem).filter(
        Viagem.data == passagem_data.data_viagem,
        Viagem.horario == passagem_data.horario,
        Viagem.motorista_id == passagem_data.motorista_id
    ).first()

    if viagem:
        # Viagem existe - incrementar contadores
        viagem.total_passageiros += 1
        viagem.valor_total += local.valor
    else:
        # Criar nova viagem
        nova_viagem = Viagem(
            data=passagem_data.data_viagem,
            horario=passagem_data.horario,
            motorista_id=passagem_data.motorista_id,
            total_passageiros=1,
            valor_total=local.valor,
            atendente_id=current_user.id,
            status="PENDENTE"
        )
        db.add(nova_viagem)

    db.commit()
    db.refresh(passagem)

    # Gera o PDF
    pdf_base64 = pdf_service.gerar_passagem_pdf(
        numero=passagem.numero,
        cliente_nome=cliente.nome,
        cidade=cidade.nome,
        local_embarque=local.nome,
        endereco_embarque=endereco_embarque,
        data_viagem=passagem.data_viagem.strftime("%d/%m/%Y"),
        horario=passagem.horario.strftime("%H:%M"),
        valor=passagem.valor,
        forma_pagamento=passagem.forma_pagamento,
        data_emissao=passagem.data_emissao,
        atendente_nome=current_user.nome
    )

    return PassagemEmitidaResponse(
        passagem=PassagemResponse.model_validate(passagem),
        pdf_base64=pdf_base64
    )


@router.get("/{passagem_id}", response_model=PassagemDetalhada)
def buscar_passagem(
    passagem_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Busca uma passagem por ID com todos os dados relacionados

    Args:
        passagem_id: ID da passagem
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Dados detalhados da passagem

    Raises:
        HTTPException 404: Se a passagem não for encontrada
    """
    passagem = db.query(Passagem).filter(Passagem.id == passagem_id).first()

    if not passagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passagem não encontrada"
        )

    # Carrega dados relacionados
    cliente = db.query(Cliente).filter(Cliente.id == passagem.cliente_id).first()
    local = db.query(LocalEmbarque).filter(LocalEmbarque.id == passagem.local_embarque_id).first()
    cidade = db.query(Cidade).filter(Cidade.id == local.cidade_id).first()
    motorista = db.query(Motorista).filter(Motorista.id == passagem.motorista_id).first()
    proprietario = db.query(Proprietario).filter(Proprietario.id == motorista.proprietario_id).first()
    atendente = db.query(Usuario).filter(Usuario.id == passagem.atendente_id).first()

    return PassagemDetalhada(
        id=passagem.id,
        numero=passagem.numero,
        data_viagem=passagem.data_viagem,
        horario=passagem.horario,
        valor=passagem.valor,
        forma_pagamento=passagem.forma_pagamento,
        status=passagem.status,
        data_emissao=passagem.data_emissao,
        cliente_nome=cliente.nome,
        cliente_telefone=cliente.telefone,
        cidade=cidade.nome,
        local_embarque=local.nome,
        endereco_embarque=passagem.endereco_embarque,
        motorista_nome=motorista.nome,
        proprietario_nome=proprietario.nome,
        atendente_nome=atendente.nome
    )


@router.get("/{passagem_id}/pdf")
def gerar_pdf_passagem(
    passagem_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera o PDF de uma passagem existente

    Args:
        passagem_id: ID da passagem
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        PDF da passagem

    Raises:
        HTTPException 404: Se a passagem não for encontrada
    """
    passagem = db.query(Passagem).filter(Passagem.id == passagem_id).first()

    if not passagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passagem não encontrada"
        )

    # Carrega dados relacionados
    cliente = db.query(Cliente).filter(Cliente.id == passagem.cliente_id).first()
    local = db.query(LocalEmbarque).filter(LocalEmbarque.id == passagem.local_embarque_id).first()
    cidade = db.query(Cidade).filter(Cidade.id == local.cidade_id).first()
    atendente = db.query(Usuario).filter(Usuario.id == passagem.atendente_id).first()

    # Gera o PDF
    pdf_base64 = pdf_service.gerar_passagem_pdf(
        numero=passagem.numero,
        cliente_nome=cliente.nome,
        cidade=cidade.nome,
        local_embarque=local.nome,
        endereco_embarque=passagem.endereco_embarque or "",
        data_viagem=passagem.data_viagem.strftime("%d/%m/%Y"),
        horario=passagem.horario.strftime("%H:%M"),
        valor=passagem.valor,
        forma_pagamento=passagem.forma_pagamento,
        data_emissao=passagem.data_emissao,
        atendente_nome=atendente.nome
    )

    # Decodifica base64 para bytes
    pdf_bytes = base64.b64decode(pdf_base64)

    # Retorna como PDF
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=passagem_{passagem.numero}.pdf"
        }
    )


@router.get("/dia/{data}", response_model=list[PassagemListItem])
def listar_passagens_dia(
    data: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todas as passagens de um dia específico

    Args:
        data: Data a ser consultada (YYYY-MM-DD)
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Lista de passagens do dia
    """
    passagens = db.query(Passagem).filter(
        Passagem.data_viagem == data
    ).order_by(Passagem.horario, Passagem.numero).all()

    result = []
    for p in passagens:
        cliente = db.query(Cliente).filter(Cliente.id == p.cliente_id).first()
        result.append(PassagemListItem(
            id=p.id,
            numero=p.numero,
            cliente_nome=cliente.nome,
            data_viagem=p.data_viagem,
            horario=p.horario,
            valor=p.valor,
            status=p.status
        ))

    return result


# ==================== CANCELAMENTO E TRANSFERÊNCIA ====================

@router.put("/{passagem_id}/cancelar", response_model=PassagemAlteradaResponse)
def cancelar_passagem(
    passagem_id: int,
    dados: PassagemCancelar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cancela uma passagem existente
    
    A passagem permanece no sistema com status CANCELADA para histórico.
    A viagem associada tem seus contadores atualizados.
    
    Args:
        passagem_id: ID da passagem a cancelar
        dados: Dados do cancelamento (motivo opcional)
        db: Sessão do banco de dados
        current_user: Usuário autenticado
    
    Returns:
        Dados da passagem cancelada
    
    Raises:
        HTTPException 404: Se a passagem não for encontrada
        HTTPException 400: Se a passagem já foi cancelada ou utilizada
    """
    passagem = db.query(Passagem).filter(Passagem.id == passagem_id).first()
    
    if not passagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passagem não encontrada"
        )
    
    if passagem.status == "CANCELADA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passagem já está cancelada"
        )
    
    if passagem.status == "UTILIZADA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cancelar uma passagem já utilizada"
        )
    
    # Guarda dados originais se ainda não foram guardados
    if not passagem.data_original:
        passagem.data_original = passagem.data_viagem
        passagem.horario_original = passagem.horario
        passagem.motorista_original_id = passagem.motorista_id
    
    # Atualiza status e dados de alteração
    passagem.status = "CANCELADA"
    passagem.data_cancelamento = datetime.now()
    passagem.motivo_alteracao = dados.motivo
    passagem.alterado_por_id = current_user.id
    
    # Atualiza contadores da viagem (decrementa)
    _atualizar_viagem_contadores(
        db=db,
        data=passagem.data_viagem,
        horario=passagem.horario,
        motorista_id=passagem.motorista_id,
        delta_passageiros=-1,
        delta_valor=-float(passagem.valor)
    )
    
    db.commit()
    db.refresh(passagem)
    
    return PassagemAlteradaResponse(
        id=passagem.id,
        numero=passagem.numero,
        status=passagem.status,
        data_viagem=passagem.data_viagem,
        horario=passagem.horario,
        data_original=passagem.data_original,
        horario_original=passagem.horario_original,
        motivo_alteracao=passagem.motivo_alteracao,
        mensagem="Passagem cancelada com sucesso"
    )


@router.put("/{passagem_id}/transferir", response_model=PassagemAlteradaResponse)
def transferir_passagem(
    passagem_id: int,
    dados: PassagemTransferir,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Transfere uma passagem para outra data/horário/motorista
    
    A passagem é movida para a nova data, e a viagem original tem
    seus contadores decrementados. Uma nova viagem é criada ou atualizada.
    
    Args:
        passagem_id: ID da passagem a transferir
        dados: Dados da transferência (nova data, horário, motorista)
        db: Sessão do banco de dados
        current_user: Usuário autenticado
    
    Returns:
        Dados da passagem transferida
    
    Raises:
        HTTPException 404: Se a passagem ou motorista não forem encontrados
        HTTPException 400: Se a passagem já foi cancelada ou utilizada
    """
    passagem = db.query(Passagem).filter(Passagem.id == passagem_id).first()
    
    if not passagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passagem não encontrada"
        )
    
    if passagem.status == "CANCELADA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível transferir uma passagem cancelada"
        )
    
    if passagem.status == "UTILIZADA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível transferir uma passagem já utilizada"
        )
    
    # Valida novo motorista
    novo_motorista = db.query(Motorista).filter(Motorista.id == dados.novo_motorista_id).first()
    if not novo_motorista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Novo motorista não encontrado"
        )
    
    # Guarda dados originais (apenas na primeira alteração)
    if not passagem.data_original:
        passagem.data_original = passagem.data_viagem
        passagem.horario_original = passagem.horario
        passagem.motorista_original_id = passagem.motorista_id
    
    # Decrementa contadores da viagem original
    _atualizar_viagem_contadores(
        db=db,
        data=passagem.data_viagem,
        horario=passagem.horario,
        motorista_id=passagem.motorista_id,
        delta_passageiros=-1,
        delta_valor=-float(passagem.valor)
    )
    
    # Atualiza passagem com novos dados
    passagem.data_viagem = dados.nova_data
    passagem.horario = dados.novo_horario
    passagem.motorista_id = dados.novo_motorista_id
    passagem.status = "EMITIDA"  # Volta para EMITIDA na nova data
    passagem.data_cancelamento = datetime.now()  # Registra momento da alteração
    passagem.motivo_alteracao = dados.motivo
    passagem.alterado_por_id = current_user.id
    
    # Busca ou cria viagem para nova data/horário
    viagem_nova = db.query(Viagem).filter(
        Viagem.data == dados.nova_data,
        Viagem.horario == dados.novo_horario,
        Viagem.motorista_id == dados.novo_motorista_id
    ).first()
    
    if viagem_nova:
        # Incrementa contadores
        viagem_nova.total_passageiros += 1
        viagem_nova.valor_total += passagem.valor
    else:
        # Cria nova viagem
        nova_viagem = Viagem(
            data=dados.nova_data,
            horario=dados.novo_horario,
            motorista_id=dados.novo_motorista_id,
            total_passageiros=1,
            valor_total=passagem.valor,
            atendente_id=current_user.id,
            status="PENDENTE"
        )
        db.add(nova_viagem)
    
    db.commit()
    db.refresh(passagem)
    
    return PassagemAlteradaResponse(
        id=passagem.id,
        numero=passagem.numero,
        status=passagem.status,
        data_viagem=passagem.data_viagem,
        horario=passagem.horario,
        data_original=passagem.data_original,
        horario_original=passagem.horario_original,
        motivo_alteracao=passagem.motivo_alteracao,
        mensagem=f"Passagem transferida para {dados.nova_data.strftime('%d/%m/%Y')} às {dados.novo_horario.strftime('%H:%M')}"
    )
