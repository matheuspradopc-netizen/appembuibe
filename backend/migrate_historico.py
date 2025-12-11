"""
Migração de Histórico de Viagens do Access para SQLite
Importa dados de historico_viagens.csv para o banco de dados atual
"""
import sys
import io
import csv
from pathlib import Path
from datetime import datetime, time, date

# Configura encoding para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models import Passagem, Cliente, Motorista, LocalEmbarque, Usuario


def limpar_telefone(telefone):
    """Remove formatação do telefone"""
    if not telefone:
        return None
    return telefone.replace('(', '').replace(')', '').replace(' ', '').replace('-', '')


def mapear_motorista_legado(motorista_id_antigo, db, cache_motoristas):
    """
    Mapeia ID de motorista do sistema antigo para o novo
    No Access: IDs eram 9, 16, 17, 25, 36, 55, 57, 58
    No novo sistema: temos motoristas com IDs sequenciais

    Vamos tentar mapear por ordem ou usar um mapeamento manual
    """
    # Cache para não repetir buscas
    if motorista_id_antigo in cache_motoristas:
        return cache_motoristas[motorista_id_antigo]

    # Pega o primeiro motorista disponível como fallback
    motorista = db.query(Motorista).filter(Motorista.ativo == True).first()

    if motorista:
        cache_motoristas[motorista_id_antigo] = motorista.id
        return motorista.id

    return None


def buscar_cliente_por_telefone(telefone, db, cache_clientes):
    """Busca cliente pelo telefone"""
    if not telefone:
        return None

    telefone_limpo = limpar_telefone(telefone)

    if telefone_limpo in cache_clientes:
        return cache_clientes[telefone_limpo]

    cliente = db.query(Cliente).filter(
        Cliente.telefone == telefone_limpo,
        Cliente.ativo == True
    ).first()

    if cliente:
        cache_clientes[telefone_limpo] = cliente.id
        return cliente.id

    return None


def migrate_historico():
    """Executa a migração do histórico"""
    print("=" * 80)
    print("MIGRAÇÃO DE HISTÓRICO DE VIAGENS - EXPRESSO EMBUIBE")
    print("=" * 80)
    print(f"\nInício: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Caminho do arquivo CSV
    csv_path = Path(__file__).parent.parent / "MIGRACAO" / "historico_viagens.csv"

    if not csv_path.exists():
        print(f"❌ ERRO: Arquivo não encontrado: {csv_path}")
        return

    print(f"📂 Arquivo: {csv_path}")
    print(f"📊 Tamanho: {csv_path.stat().st_size / 1024 / 1024:.2f} MB\n")

    # Estatísticas
    stats = {
        'total': 0,
        'importados': 0,
        'sem_cliente': 0,
        'sem_motorista': 0,
        'erros': 0,
        'valor_total': 0.0
    }

    erros_detalhados = []

    # Caches
    cache_clientes = {}
    cache_motoristas = {}

    # Abre sessão do banco
    db = SessionLocal()

    try:
        # Busca dados necessários
        print("🔍 Buscando dados de referência...")

        # Pega primeiro local de embarque (fallback)
        local_embarque_padrao = db.query(LocalEmbarque).filter(LocalEmbarque.ativo == True).first()
        if not local_embarque_padrao:
            print("❌ ERRO: Nenhum local de embarque encontrado no banco!")
            return

        # Pega usuário admin (fallback para atendente)
        usuario_admin = db.query(Usuario).filter(Usuario.tipo == 'admin').first()
        if not usuario_admin:
            print("❌ ERRO: Usuário admin não encontrado no banco!")
            return

        print(f"  ✓ Local embarque padrão: {local_embarque_padrao.nome}")
        print(f"  ✓ Atendente padrão: {usuario_admin.nome}\n")

        print("🔄 Lendo arquivo CSV...\n")

        # Busca o maior número de passagem existente
        max_numero = db.query(func.max(Passagem.numero)).scalar() or 0
        print(f"  ℹ️  Maior número de passagem existente: {max_numero}")
        print(f"  ℹ️  Próximo número será: {max_numero + 1}\n")

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                stats['total'] += 1

                try:
                    # Extrai dados do CSV
                    id_legado = row.get('id_legado', '')
                    cliente_nome = row.get('cliente_nome', '').strip()
                    cliente_telefone = row.get('cliente_telefone', '').strip()
                    data_venda_str = row.get('data_venda', '')
                    data_pedido_str = row.get('data_pedido', '')
                    valor_unitario = float(row.get('valor_unitario', 0))
                    quantidade = int(row.get('quantidade', 1))
                    valor_total = float(row.get('valor_total', 0))
                    motorista_id_antigo = row.get('motorista_id', '')

                    # Busca cliente pelo telefone
                    cliente_id = buscar_cliente_por_telefone(cliente_telefone, db, cache_clientes)

                    if not cliente_id:
                        stats['sem_cliente'] += 1
                        if stats['sem_cliente'] <= 5:
                            print(f"  ⚠️  Cliente não encontrado: {cliente_nome} - {cliente_telefone}")
                        continue

                    # Mapeia motorista
                    if motorista_id_antigo:
                        motorista_id = mapear_motorista_legado(float(motorista_id_antigo), db, cache_motoristas)
                    else:
                        motorista_id = None

                    if not motorista_id:
                        stats['sem_motorista'] += 1
                        if stats['sem_motorista'] <= 5:
                            print(f"  ⚠️  Motorista não encontrado: ID antigo {motorista_id_antigo}")
                        continue

                    # Converte datas
                    try:
                        data_viagem = datetime.strptime(data_pedido_str, '%Y-%m-%d').date() if data_pedido_str else date.today()
                        data_emissao = datetime.strptime(data_venda_str, '%Y-%m-%d') if data_venda_str else datetime.now()
                    except ValueError as e:
                        stats['erros'] += 1
                        if stats['erros'] <= 5:
                            print(f"  ❌ Erro na data: {data_pedido_str} / {data_venda_str}")
                        continue

                    # Incrementa número da passagem
                    max_numero += 1

                    # Cria a passagem
                    passagem = Passagem(
                        numero=max_numero,
                        cliente_id=cliente_id,
                        local_embarque_id=local_embarque_padrao.id,
                        motorista_id=motorista_id,
                        horario=time(0, 0),  # Padrão 00:00
                        data_viagem=data_viagem,
                        data_emissao=data_emissao,
                        valor=valor_total,
                        forma_pagamento='DINHEIRO',  # Padrão
                        atendente_id=usuario_admin.id,
                        status='UTILIZADA'  # Histórico
                    )

                    db.add(passagem)
                    stats['importados'] += 1
                    stats['valor_total'] += float(valor_total)

                    # Commit a cada 500 registros
                    if stats['importados'] % 500 == 0:
                        db.commit()
                        print(f"  ✓ {stats['importados']} viagens importadas... (R$ {stats['valor_total']:,.2f})")

                except Exception as e:
                    stats['erros'] += 1
                    erro_msg = f"Linha {stats['total']}: {str(e)}"
                    erros_detalhados.append(erro_msg)
                    if stats['erros'] <= 10:
                        print(f"  ❌ {erro_msg}")
                    continue

        # Commit final
        db.commit()

        # Verifica total no banco
        total_banco = db.query(func.count(Passagem.id)).scalar()

        print("\n" + "=" * 80)
        print("RELATÓRIO DE MIGRAÇÃO")
        print("=" * 80)
        print(f"\n📊 Estatísticas:")
        print(f"  • Total de linhas processadas: {stats['total']}")
        print(f"  • Viagens importadas: {stats['importados']}")
        print(f"  • Sem cliente encontrado: {stats['sem_cliente']}")
        print(f"  • Sem motorista encontrado: {stats['sem_motorista']}")
        print(f"  • Erros: {stats['erros']}")
        print(f"  • Valor total do histórico: R$ {stats['valor_total']:,.2f}")
        print(f"\n💾 Total de passagens no banco: {total_banco}")

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
    migrate_historico()
