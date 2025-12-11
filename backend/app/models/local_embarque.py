"""
Model de Locais de Embarque - Expresso Embuibe
Gerencia pontos de embarque com valores
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class LocalEmbarque(Base):
    __tablename__ = "locais_embarque"

    id = Column(Integer, primary_key=True, index=True)
    cidade_id = Column(Integer, ForeignKey("cidades.id"), nullable=False)
    nome = Column(String(150), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    cidade = relationship("Cidade", back_populates="locais_embarque")
    passagens = relationship("Passagem", back_populates="local_embarque")

    def __repr__(self):
        return f"<LocalEmbarque(id={self.id}, nome='{self.nome}', valor={self.valor})>"
