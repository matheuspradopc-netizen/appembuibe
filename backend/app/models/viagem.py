"""
Model de Viagens - Expresso Embuibe
Gerencia registro de saída das viagens
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, Date, Time, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Viagem(Base):
    __tablename__ = "viagens"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False, index=True)
    horario = Column(Time, nullable=False)
    motorista_id = Column(Integer, ForeignKey("motoristas.id"), nullable=False)
    total_passageiros = Column(Integer, nullable=False, default=0)
    valor_total = Column(Numeric(10, 2), nullable=False, default=0)
    atendente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    status = Column(String(20), nullable=False, default="PENDENTE")  # PENDENTE ou SAIU
    data_saida = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    motorista = relationship("Motorista", back_populates="viagens")
    atendente = relationship("Usuario")

    def __repr__(self):
        return f"<Viagem(id={self.id}, data={self.data}, motorista_id={self.motorista_id}, passageiros={self.total_passageiros})>"
