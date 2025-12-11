"""
Script de Seed - Expresso Embuibe
Popula o banco de dados com dados iniciais
"""
import sys
import io
from pathlib import Path

# Configura encoding para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

import bcrypt
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import (
    Usuario, Cliente, Proprietario, Motorista,
    Cidade, LocalEmbarque, Passagem, Viagem
)


def hash_password(password: str) -> str:
    """Hash de senha usando bcrypt"""
    # Converte a senha para bytes e gera o hash
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def seed_usuarios(db: Session):
    """Popula tabela de usuários"""
    print("Populando usuários...")

    usuarios = [
        {
            "nome": "Administrador",
            "login": "admin",
            "senha": "embuibe@2025",
            "tipo": "admin"
        },
        {
            "nome": "Mariana",
            "login": "mariana",
            "senha": "2107",
            "tipo": "atendente"
        },
        {
            "nome": "Daniela",
            "login": "daniela",
            "senha": "2106",
            "tipo": "atendente"
        }
    ]

    for user_data in usuarios:
        # Verifica se já existe
        existing = db.query(Usuario).filter(Usuario.login == user_data["login"]).first()
        if existing:
            print(f"  Usuário '{user_data['login']}' já existe, pulando...")
            continue

        usuario = Usuario(
            nome=user_data["nome"],
            login=user_data["login"],
            senha_hash=hash_password(user_data["senha"]),
            tipo=user_data["tipo"],
            ativo=True
        )
        db.add(usuario)
        print(f"  ✓ Usuário '{user_data['nome']}' criado")

    db.commit()


def seed_proprietarios_motoristas(db: Session):
    """Popula tabela de proprietários e motoristas"""
    print("Populando proprietários e motoristas...")

    dados = [
        {"proprietario": "Adelson JR", "motorista": "Mauro", "vagas": 15},
        {"proprietario": "Walter", "motorista": "Walter", "vagas": 14},
        {"proprietario": "Junior", "motorista": "Zacarias", "vagas": 14},
        {"proprietario": "Juninho", "motorista": "Pity", "vagas": 14},
        {"proprietario": "Gilson", "motorista": "Zacarias2", "vagas": 14},
        {"proprietario": "Anderson", "motorista": "Geraldo", "vagas": 15},
        {"proprietario": "Denilson Drun", "motorista": "Patrícia", "vagas": 15},
    ]

    for item in dados:
        # Verifica/cria proprietário
        proprietario = db.query(Proprietario).filter(
            Proprietario.nome == item["proprietario"]
        ).first()

        if not proprietario:
            proprietario = Proprietario(nome=item["proprietario"], ativo=True)
            db.add(proprietario)
            db.flush()  # Para obter o ID
            print(f"  ✓ Proprietário '{item['proprietario']}' criado")

        # Verifica se motorista já existe
        existing = db.query(Motorista).filter(
            Motorista.nome == item["motorista"]
        ).first()

        if existing:
            print(f"  Motorista '{item['motorista']}' já existe, pulando...")
            continue

        # Cria motorista
        motorista = Motorista(
            nome=item["motorista"],
            proprietario_id=proprietario.id,
            vagas=item["vagas"],
            ativo=True
        )
        db.add(motorista)
        print(f"  ✓ Motorista '{item['motorista']}' criado (Proprietário: {item['proprietario']})")

    db.commit()


def seed_cidades(db: Session):
    """Popula tabela de cidades"""
    print("Populando cidades...")

    cidades = [
        {"nome": "Peruíbe", "ordem": 1},
        {"nome": "Itanhaém", "ordem": 2},
        {"nome": "Mongaguá", "ordem": 3},
        {"nome": "Praia Grande", "ordem": 4},
        {"nome": "São Vicente", "ordem": 5},
    ]

    for cidade_data in cidades:
        # Verifica se já existe
        existing = db.query(Cidade).filter(Cidade.nome == cidade_data["nome"]).first()
        if existing:
            print(f"  Cidade '{cidade_data['nome']}' já existe, pulando...")
            continue

        cidade = Cidade(nome=cidade_data["nome"], ordem=cidade_data["ordem"])
        db.add(cidade)
        print(f"  ✓ Cidade '{cidade_data['nome']}' criada")

    db.commit()


def seed_locais_embarque(db: Session):
    """Popula tabela de locais de embarque"""
    print("Populando locais de embarque...")

    # Mapeia nome da cidade para locais
    locais_por_cidade = {
        "Peruíbe": [
            {"local": "Centro", "valor": 65.00},
            {"local": "Casa", "valor": 65.00},
            {"local": "Santa Cruz", "valor": 65.00},
        ],
        "Itanhaém": [
            {"local": "Gaivotas", "valor": 65.00},
            {"local": "Bopiranga", "valor": 65.00},
            {"local": "Rodoviária", "valor": 65.00},
            {"local": "Santa Julia", "valor": 65.00},
            {"local": "Jardim Itanhaém", "valor": 65.00},
            {"local": "Cabuçu", "valor": 60.00},
            {"local": "Suarão", "valor": 60.00},
            {"local": "Jardim Suarão", "valor": 60.00},
            {"local": "Jardim São João", "valor": 65.00},
            {"local": "Jardim São Fernando", "valor": 65.00},
            {"local": "Jardim Grandesp", "valor": 65.00},
            {"local": "Tupi", "valor": 65.00},
            {"local": "Cibratel 2", "valor": 65.00},
            {"local": "Cibratel", "valor": 65.00},
            {"local": "Savoy", "valor": 60.00},
            {"local": "Nova Itanhaém", "valor": 60.00},
            {"local": "Jequitibá", "valor": 60.00},
            {"local": "Vila Loty", "valor": 60.00},
            {"local": "Campos Eliseos", "valor": 60.00},
        ],
        "Mongaguá": [
            {"local": "Florida Mirim", "valor": 60.00},
            {"local": "Agenor de Campos", "valor": 60.00},
            {"local": "Jussara", "valor": 60.00},
            {"local": "Itaóca", "valor": 60.00},
            {"local": "Jardim Santa Eugênia", "valor": 60.00},
            {"local": "Jardim Praia Grande", "valor": 60.00},
            {"local": "Nossa Sra de Fátima", "valor": 60.00},
            {"local": "Vera Cruz", "valor": 60.00},
            {"local": "Pedreira", "valor": 60.00},
        ],
        "Praia Grande": [
            {"local": "Jardim Alice", "valor": 60.00},
            {"local": "Cidade da Criança", "valor": 60.00},
            {"local": "Jardim Solemar", "valor": 60.00},
            {"local": "Jardim Samambaia", "valor": 60.00},
            {"local": "Flórida", "valor": 60.00},
            {"local": "Jardim Princesa", "valor": 60.00},
            {"local": "Jardim Real", "valor": 60.00},
            {"local": "Jardim Imperador", "valor": 60.00},
            {"local": "Vila Caiçara", "valor": 60.00},
            {"local": "Jardim Melvi", "valor": 60.00},
            {"local": "Curva do S", "valor": 60.00},
            {"local": "CDP", "valor": 60.00},
        ],
        "São Vicente": [
            {"local": "Jardim Samaritá", "valor": 60.00},
            {"local": "Rio Branco", "valor": 60.00},
            {"local": "Parque das Bandeiras", "valor": 60.00},
            {"local": "Presídio", "valor": 60.00},
            {"local": "Humaitá", "valor": 60.00},
            {"local": "Vale Verde", "valor": 60.00},
        ],
    }

    for cidade_nome, locais in locais_por_cidade.items():
        # Busca a cidade
        cidade = db.query(Cidade).filter(Cidade.nome == cidade_nome).first()
        if not cidade:
            print(f"  ERRO: Cidade '{cidade_nome}' não encontrada!")
            continue

        for local_data in locais:
            # Verifica se já existe
            existing = db.query(LocalEmbarque).filter(
                LocalEmbarque.cidade_id == cidade.id,
                LocalEmbarque.nome == local_data["local"]
            ).first()

            if existing:
                continue

            local = LocalEmbarque(
                cidade_id=cidade.id,
                nome=local_data["local"],
                valor=local_data["valor"],
                ativo=True
            )
            db.add(local)

        db.commit()
        print(f"  ✓ Locais de '{cidade_nome}' criados ({len(locais)} locais)")


def main():
    """Função principal de seed"""
    print("=" * 60)
    print("SEED DO BANCO DE DADOS - EXPRESSO EMBUIBE")
    print("=" * 60)

    # Cria as tabelas se não existirem
    print("\nCriando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tabelas criadas/verificadas")

    # Cria sessão do banco
    db = SessionLocal()

    try:
        # Executa seeds na ordem correta (respeitando FKs)
        seed_usuarios(db)
        seed_cidades(db)
        seed_proprietarios_motoristas(db)
        seed_locais_embarque(db)

        print("\n" + "=" * 60)
        print("✓ SEED CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("\nCredenciais de acesso:")
        print("\nAdministrador:")
        print("  Login: admin")
        print("  Senha: embuibe@2025")
        print("\nAtendentes:")
        print("  Mariana - Login: mariana | Senha: 2107")
        print("  Daniela - Login: daniela | Senha: 2106")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ ERRO durante o seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
