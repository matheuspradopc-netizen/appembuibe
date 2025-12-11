"""
Model de Passagens - Expresso Embuibe
Gerencia passagens emitidas
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Date, Time
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
    status = Column(String(20), default="EMITIDA", nullable=False)  # EMITIDA, CANCELADA, UTILIZADA
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="passagens")
    local_embarque = relationship("LocalEmbarque", back_populates="passagens")
    motorista = relationship("Motorista", back_populates="passagens")
    atendente = relationship("Usuario")

    def __repr__(self):
        return f"<Passagem(id={self.id}, numero={self.numero}, cliente_id={self.cliente_id})>"
