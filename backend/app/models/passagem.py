"""
Model de Passagens - Expresso Embuibe
Gerencia passagens emitidas
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Date, Time, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Passagem(Base):
    __tablename__ = "passagens"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, unique=True, nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    local_embarque_id = Column(Integer, ForeignKey("locais_embarque.id"), nullable=False)
    motorista_id = Column(Integer, ForeignKey("motoristas.id"), nullable=False, index=True)
    horario = Column(Time, nullable=False, index=True)
    data_viagem = Column(Date, nullable=False, index=True)
    data_emissao = Column(DateTime(timezone=True), server_default=func.now())
    valor = Column(Numeric(10, 2), nullable=False)
    forma_pagamento = Column(String(20), nullable=False)  # DINHEIRO, CARTAO, PIX
    atendente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    status = Column(String(20), default="EMITIDA", nullable=False)  # EMITIDA, CANCELADA, TRANSFERIDA, UTILIZADA
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Endereço de embarque (pode ser diferente do endereço cadastrado do cliente)
    endereco_embarque = Column(Text, nullable=True)  # Endereço onde a van vai buscar
    
    # Campos para cancelamento/transferência
    data_original = Column(Date, nullable=True)  # Data original antes de transferir
    horario_original = Column(Time, nullable=True)  # Horário original antes de transferir
    motorista_original_id = Column(Integer, ForeignKey("motoristas.id"), nullable=True)  # Motorista original
    data_cancelamento = Column(DateTime(timezone=True), nullable=True)  # Quando foi cancelada/transferida
    motivo_alteracao = Column(Text, nullable=True)  # Motivo do cancelamento ou transferência
    alterado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)  # Quem cancelou/transferiu

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="passagens")
    local_embarque = relationship("LocalEmbarque", back_populates="passagens")
    motorista = relationship("Motorista", foreign_keys=[motorista_id], back_populates="passagens")
    motorista_original = relationship("Motorista", foreign_keys=[motorista_original_id])
    atendente = relationship("Usuario", foreign_keys=[atendente_id])
    alterado_por = relationship("Usuario", foreign_keys=[alterado_por_id])

    def __repr__(self):
        return f"<Passagem(id={self.id}, numero={self.numero}, cliente_id={self.cliente_id}, status={self.status})>"
