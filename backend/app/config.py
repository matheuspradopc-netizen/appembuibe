"""
Configurações do sistema - Expresso Embuibe
Gerencia todas as variáveis de ambiente e configurações da aplicação
"""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas do arquivo .env
    """
    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Application
    APP_NAME: str = "Expresso Embuibe"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Configurações de Negócio
    DESTINO_PADRAO: str = "Embu das Artes"
    NUMERO_PASSAGEM_INICIAL: int = 30000

    class Config:
        # Procura o .env na raiz do projeto (pasta pai da pasta backend)
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = True


# Instância global das configurações
settings = Settings()
