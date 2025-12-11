"""
Model de Proprietários - Expresso Embuibe
Gerencia donos das vans
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Proprietario(Base):
    __tablename__ = "proprietarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    motoristas = relationship("Motorista", back_populates="proprietario")

    def __repr__(self):
        return f"<Proprietario(id={self.id}, nome='{self.nome}')>"
