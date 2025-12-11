"""
Script de Migração - Adiciona colunas de cancelamento/transferência
Execute este script para atualizar o banco de dados existente
"""
import sqlite3
import os

def migrate():
    # Caminho do banco
    db_path = os.path.join(os.path.dirname(__file__), 'expresso_embuibe.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    print(f"📦 Conectando ao banco: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Lista de colunas a adicionar na tabela passagens
    colunas_passagens = [
        ("endereco_embarque", "TEXT"),
        ("data_original", "DATE"),
        ("horario_original", "TIME"),
        ("motorista_original_id", "INTEGER"),
        ("data_cancelamento", "DATETIME"),
        ("motivo_alteracao", "TEXT"),
        ("alterado_por_id", "INTEGER"),
    ]
    
    print("\n🔧 Verificando e adicionando colunas na tabela 'passagens'...")
    
    # Verifica colunas existentes
    cursor.execute("PRAGMA table_info(passagens)")
    colunas_existentes = [col[1] for col in cursor.fetchall()]
    print(f"   Colunas existentes: {colunas_existentes}")
    
    for coluna, tipo in colunas_passagens:
        if coluna not in colunas_existentes:
            try:
                cursor.execute(f"ALTER TABLE passagens ADD COLUMN {coluna} {tipo}")
                print(f"   ✅ Coluna '{coluna}' adicionada com sucesso")
            except sqlite3.OperationalError as e:
                print(f"   ⚠️ Erro ao adicionar '{coluna}': {e}")
        else:
            print(f"   ℹ️ Coluna '{coluna}' já existe")
    
    # Atualiza status para incluir novos valores possíveis
    print("\n🔧 Verificando valores de status...")
    cursor.execute("SELECT DISTINCT status FROM passagens")
    status_existentes = [row[0] for row in cursor.fetchall()]
    print(f"   Status existentes: {status_existentes}")
    
    # Commit das alterações
    conn.commit()
    print("\n✅ Migração concluída com sucesso!")
    
    # Mostra estrutura atualizada
    print("\n📋 Estrutura atualizada da tabela 'passagens':")
    cursor.execute("PRAGMA table_info(passagens)")
    for col in cursor.fetchall():
        print(f"   - {col[1]} ({col[2]})")
    
    conn.close()
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("MIGRAÇÃO - Expresso Embuibe")
    print("Adiciona suporte a cancelamento/transferência")
    print("=" * 50)
    migrate()
