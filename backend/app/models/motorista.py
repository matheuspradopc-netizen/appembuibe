"""
Model de Motoristas - Expresso Embuibe
Gerencia motoristas vinculados aos proprietários
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Motorista(Base):
    __tablename__ = "motoristas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    proprietario_id = Column(Integer, ForeignKey("proprietarios.id"), nullable=False)
    vagas = Column(Integer, nullable=False, default=14)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    proprietario = relationship("Proprietario", back_populates="motoristas")
    passagens = relationship("Passagem", back_populates="motorista", foreign_keys="[Passagem.motorista_id]")
    viagens = relationship("Viagem", back_populates="motorista")

    def __repr__(self):
        return f"<Motorista(id={self.id}, nome='{self.nome}', vagas={self.vagas})>"
