"""
Script para criar as tabelas do banco de dados - Expresso Embuibe
"""
import sys
import io
from app.database import engine, Base
from app import models

# Configura encoding para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_tables():
    """
    Cria todas as tabelas no banco de dados
    """
    print("=" * 60)
    print("CRIANDO TABELAS DO BANCO DE DADOS")
    print("=" * 60)

    try:
        # Importa todos os models para garantir que estão registrados
        print("\nImportando models...")
        print(f"OK - {len(Base.metadata.tables)} tabelas encontradas")

        # Cria todas as tabelas
        print("\nCriando tabelas no banco de dados...")
        Base.metadata.create_all(bind=engine)

        print("\n" + "=" * 60)
        print("SUCESSO! TABELAS CRIADAS COM SUCESSO!")
        print("=" * 60)

        print("\nTabelas criadas:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")

        print("\n" + "=" * 60)
        print("Proximo passo: executar o seed de dados")
        print("Comando: python seed_data.py")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("ERRO AO CRIAR TABELAS")
        print("=" * 60)
        print(f"\nErro: {e}")
        raise


if __name__ == "__main__":
    create_tables()
