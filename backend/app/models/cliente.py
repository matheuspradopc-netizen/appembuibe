"""
Model de Clientes - Expresso Embuibe
Gerencia passageiros cadastrados no sistema
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False, index=True)
    telefone = Column(String(20), nullable=False, index=True)
    cidade = Column(String(100), nullable=False)
    bairro = Column(String(100), nullable=True)
    endereco = Column(String(255), nullable=True)
    cep = Column(String(10), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    passagens = relationship("Passagem", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome='{self.nome}', telefone='{self.telefone}')>"
