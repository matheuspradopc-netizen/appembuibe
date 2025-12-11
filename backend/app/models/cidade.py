"""
Model de Cidades - Expresso Embuibe
Gerencia cidades de origem
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base


class Cidade(Base):
    __tablename__ = "cidades"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    ordem = Column(Integer, default=0)

    # Relacionamentos
    locais_embarque = relationship("LocalEmbarque", back_populates="cidade")

    def __repr__(self):
        return f"<Cidade(id={self.id}, nome='{self.nome}', ordem={self.ordem})>"
