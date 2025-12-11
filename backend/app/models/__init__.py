"""
Models do sistema - Expresso Embuibe
Exporta todos os models SQLAlchemy
"""
from .usuario import Usuario
from .cliente import Cliente
from .proprietario import Proprietario
from .motorista import Motorista
from .cidade import Cidade
from .local_embarque import LocalEmbarque
from .passagem import Passagem
from .viagem import Viagem

__all__ = [
    "Usuario",
    "Cliente",
    "Proprietario",
    "Motorista",
    "Cidade",
    "LocalEmbarque",
    "Passagem",
    "Viagem",
]
