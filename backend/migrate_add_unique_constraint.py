"""
Script de migração para adicionar constraint único na tabela viagens
Garante que não existam viagens duplicadas para o mesmo data/horário/motorista
"""
import sys
import io
from sqlalchemy import text
from app.database import engine

# Configura encoding para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def migrate():
    """
    Adiciona constraint único na tabela viagens
    """
    print("=" * 60)
    print("MIGRAÇÃO: ADICIONAR CONSTRAINT ÚNICO EM VIAGENS")
    print("=" * 60)

    with engine.connect() as conn:
        try:
            # Primeiro, verifica se existem viagens duplicadas
            print("\nVerificando viagens duplicadas...")
            result = conn.execute(text("""
                SELECT data, horario, motorista_id, COUNT(*) as count
                FROM viagens
                GROUP BY data, horario, motorista_id
                HAVING COUNT(*) > 1
            """))
            duplicates = result.fetchall()

            if duplicates:
                print(f"\n⚠️  ATENÇÃO: Encontradas {len(duplicates)} combinações duplicadas!")
                print("Por favor, resolva as duplicatas manualmente antes de continuar.")
                for dup in duplicates:
                    print(f"  - Data: {dup[0]}, Horário: {dup[1]}, Motorista: {dup[2]} ({dup[3]} registros)")
                return False

            print("✅ Nenhuma duplicata encontrada")

            # Verifica se o constraint já existe
            print("\nVerificando se o constraint já existe...")

            # Para SQLite
            result = conn.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='viagens'"))
            table_sql = result.fetchone()

            if table_sql and 'uix_viagem_data_horario_motorista' in str(table_sql[0]):
                print("✅ Constraint já existe, nada a fazer")
                return True

            # Criar índice único (funciona como constraint em SQLite)
            print("\nCriando índice único...")
            conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS uix_viagem_data_horario_motorista
                ON viagens (data, horario, motorista_id)
            """))
            conn.commit()

            print("\n" + "=" * 60)
            print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 60)
            return True

        except Exception as e:
            print(f"\n❌ ERRO durante a migração: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    migrate()
