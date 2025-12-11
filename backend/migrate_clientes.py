"""
Migração de Clientes do Access para SQLite
Importa dados de clientes_migrar.csv para o banco de dados atual
"""
import sys
import io
import csv
from pathlib import Path
from datetime import datetime

# Configura encoding para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models import Cliente


def clean_phone(phone):
    """Remove formatação do telefone, mantendo apenas números"""
    if not phone:
        return None
    # Remove parênteses, espaços, hífens
    cleaned = phone.replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
    if cleaned and len(cleaned) >= 10:
        return cleaned
    return None


def migrate_clientes():
    """Executa a migração de clientes"""
    print("=" * 80)
    print("MIGRAÇÃO DE CLIENTES - EXPRESSO EMBUIBE")
    print("=" * 80)
    print(f"\nInício: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Caminho do arquivo CSV
    csv_path = Path(__file__).parent.parent / "MIGRACAO" / "clientes_migrar.csv"

    if not csv_path.exists():
        print(f"❌ ERRO: Arquivo não encontrado: {csv_path}")
        return

    print(f"📂 Arquivo: {csv_path}")
    print(f"📊 Tamanho: {csv_path.stat().st_size / 1024 / 1024:.2f} MB\n")

    # Estatísticas
    stats = {
        'total': 0,
        'importados': 0,
        'duplicados': 0,
        'erros': 0,
        'sem_telefone': 0
    }

    erros_detalhados = []

    # Abre sessão do banco
    db = SessionLocal()

    try:
        print("🔄 Lendo arquivo CSV...\n")

        with open(csv_path, 'r', encoding='utf-8') as f:
            # Usar csv.DictReader para ler o CSV
            reader = csv.DictReader(f)

            for row in reader:
                stats['total'] += 1

                try:
                    # Extrai dados do CSV
                    id_legado = row.get('id_legado', '')
                    nome = row.get('nome', '').strip()
                    telefone1 = row.get('telefone1', '').strip()
                    telefone2 = row.get('telefone2', '').strip()
                    ponto_embarque = row.get('ponto_embarque', '').strip()
                    cidade = row.get('cidade', '').strip()
                    uf = row.get('uf', '').strip()

                    # Valida nome obrigatório
                    if not nome:
                        stats['erros'] += 1
                        erros_detalhados.append(f"Linha {stats['total']}: Nome vazio")
                        continue

                    # Limpa telefone principal
                    telefone_limpo = clean_phone(telefone1)

                    if not telefone_limpo:
                        stats['sem_telefone'] += 1
                        # Mesmo sem telefone, vamos importar o cliente
                        # usando um placeholder baseado no ID legado
                        telefone_limpo = f"SEM_TELEFONE_{id_legado}"

                    # Verifica se já existe cliente com mesmo telefone
                    if not telefone_limpo.startswith('SEM_TELEFONE_'):
                        existing = db.query(Cliente).filter(
                            Cliente.telefone == telefone_limpo,
                            Cliente.ativo == True
                        ).first()

                        if existing:
                            stats['duplicados'] += 1
                            if stats['duplicados'] <= 10:  # Mostra apenas os primeiros 10
                                print(f"  ⚠️  Duplicado: {nome} - {telefone1} (já existe no banco)")
                            continue

                    # Monta endereço (obrigatório) - usa ponto_embarque ou placeholder
                    endereco_final = ponto_embarque if ponto_embarque else "A DEFINIR"

                    # Tenta extrair bairro do ponto_embarque
                    # Formato comum: "Rua X - Bairro Y" ou só "Bairro"
                    bairro_final = "A DEFINIR"
                    if ponto_embarque and '-' in ponto_embarque:
                        partes = ponto_embarque.split('-')
                        if len(partes) >= 2:
                            bairro_final = partes[1].strip()
                    elif ponto_embarque and len(ponto_embarque) < 50:
                        bairro_final = ponto_embarque.strip()

                    # Cidade (obrigatório)
                    cidade_final = cidade if cidade else "PERUIBE"

                    # CEP (obrigatório) - usa placeholder
                    cep_final = "00000-000"

                    # Cria o cliente
                    cliente = Cliente(
                        nome=nome,
                        telefone=telefone_limpo,
                        endereco=endereco_final,
                        bairro=bairro_final,
                        cidade=cidade_final,
                        cep=cep_final,
                        ativo=True
                    )

                    db.add(cliente)
                    stats['importados'] += 1

                    # Commit a cada 100 registros para evitar travamento
                    if stats['importados'] % 100 == 0:
                        db.commit()
                        print(f"  ✓ {stats['importados']} clientes importados...")

                except Exception as e:
                    stats['erros'] += 1
                    erro_msg = f"Linha {stats['total']} ({nome if 'nome' in locals() else 'N/A'}): {str(e)}"
                    erros_detalhados.append(erro_msg)
                    if stats['erros'] <= 10:  # Mostra apenas os primeiros 10 erros
                        print(f"  ❌ {erro_msg}")
                    continue

        # Commit final
        db.commit()

        # Verifica total no banco
        total_banco = db.query(func.count(Cliente.id)).filter(Cliente.ativo == True).scalar()

        print("\n" + "=" * 80)
        print("RELATÓRIO DE MIGRAÇÃO")
        print("=" * 80)
        print(f"\n📊 Estatísticas:")
        print(f"  • Total de linhas processadas: {stats['total']}")
        print(f"  • Clientes importados: {stats['importados']}")
        print(f"  • Duplicados ignorados: {stats['duplicados']}")
        print(f"  • Sem telefone: {stats['sem_telefone']}")
        print(f"  • Erros: {stats['erros']}")
        print(f"\n💾 Total de clientes ativos no banco: {total_banco}")

        if erros_detalhados and len(erros_detalhados) > 10:
            print(f"\n⚠️  Foram encontrados {len(erros_detalhados)} erros no total.")
            print(f"   Primeiros 10 erros mostrados acima.")

        print(f"\n✅ Migração concluída com sucesso!")
        print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ ERRO FATAL durante a migração: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_clientes()
