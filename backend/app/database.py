"""
Configuração do banco de dados - Expresso Embuibe
Gerencia a conexão com PostgreSQL usando SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Cria o engine do SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexões antes de usar
    pool_size=10,  # Número de conexões no pool
    max_overflow=20  # Conexões adicionais quando o pool está cheio
)

# Cria a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os models
Base = declarative_base()


def get_db():
    """
    Dependência que fornece uma sessão do banco de dados.
    A sessão é fechada automaticamente após o uso.

    Uso:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # usar db aqui
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas.
    Deve ser chamado uma vez no início da aplicação.
    """
    from . import models  # Import necessário para registrar os models
    Base.metadata.create_all(bind=engine)
