"""
Script para testar o fluxo completo do sistema
"""
import requests
from datetime import date, time

BASE_URL = "http://localhost:8001/api/v1"

print("=" * 60)
print("TESTE DO FLUXO COMPLETO - SISTEMA EXPRESSO EMBUIBE")
print("=" * 60)

# 1. Login
print("\n1. Fazendo login...")
response = requests.post(f"{BASE_URL}/auth/login", json={
    "login": "admin",
    "senha": "embuibe@2025"
})

if response.status_code != 200:
    print(f"ERRO no login: {response.text}")
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("[OK] Login bem-sucedido!")

# 2. Emitir passagem (deve criar viagem automaticamente)
print("\n2. Emitindo passagem...")
hoje = date.today().strftime("%Y-%m-%d")

passagem_data = {
    "cliente_id": 1,
    "local_embarque_id": 1,
    "motorista_id": 1,
    "horario": "14:00",
    "data_viagem": hoje,
    "forma_pagamento": "PIX"
}

response = requests.post(
    f"{BASE_URL}/passagens",
    json=passagem_data,
    headers=headers
)

if response.status_code != 201:
    print(f"ERRO ao emitir passagem: {response.text}")
    exit(1)

passagem = response.json()
print(f"[OK] Passagem #{passagem['passagem']['numero']} emitida!")
print(f"  Cliente ID: {passagem['passagem']['cliente_id']}")
print(f"  Data: {passagem['passagem']['data_viagem']}")
print(f"  Horario: {passagem['passagem']['horario']}")

# 3. Verificar se viagem foi criada automaticamente
print("\n3. Verificando se viagem foi criada automaticamente...")
response = requests.get(
    f"{BASE_URL}/relatorios/diario?data={hoje}",
    headers=headers
)

if response.status_code != 200:
    print(f"ERRO ao buscar relatório: {response.text}")
    exit(1)

relatorio = response.json()
print(f"[OK] Relatorio gerado!")
print(f"  Total de viagens: {relatorio['total_viagens']}")
print(f"  Total de passageiros: {relatorio['total_passageiros']}")
print(f"  Valor total: R$ {relatorio['total_valor']:.2f}")

if relatorio['total_viagens'] > 0:
    print(f"\n  Viagens do dia:")
    for v in relatorio['viagens']:
        print(f"    - {v['horario']} | {v['motorista']} ({v['proprietario']}) | {v['passageiros']} passageiros | Status: {v['status']}")
else:
    print("  ERRO: Nenhuma viagem encontrada!")

# 4. Confirmar saída da viagem
print("\n4. Confirmando saída da viagem...")
response = requests.post(
    f"{BASE_URL}/viagens/confirmar-saida",
    json={
        "data": hoje,
        "horario": "14:00",
        "motorista_id": 1
    },
    headers=headers
)

if response.status_code != 200:
    print(f"ERRO ao confirmar saída: {response.text}")
    # Não encerra, pode já estar confirmada
else:
    resultado = response.json()
    print(f"[OK] {resultado['mensagem']}")
    print(f"  Viagem: {resultado['viagem']['motorista']} - {resultado['viagem']['horario']}")
    print(f"  Passageiros: {resultado['viagem']['passageiros']}")
    print(f"  Status: {resultado['viagem']['status']}")

# 5. Verificar relatório atualizado
print("\n5. Verificando relatório atualizado...")
response = requests.get(
    f"{BASE_URL}/relatorios/diario?data={hoje}",
    headers=headers
)

relatorio = response.json()
print(f"[OK] Relatorio atualizado!")
print(f"  Viagens com status SAIU:")
for v in relatorio['viagens']:
    if v['status'] == 'SAIU':
        print(f"    - {v['horario']} | {v['motorista']} | Status: {v['status']}")

print("\n" + "=" * 60)
print("TESTE COMPLETO!")
print("=" * 60)
