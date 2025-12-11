# Sistema Expresso Embuibe

Sistema web para gestão de transporte de passageiros - emissão de passagens, relatórios e controle de viagens.

## Sobre o Projeto

O Sistema Expresso Embuibe é uma aplicação web desenvolvida para facilitar a gestão de viagens de transporte de passageiros na rota Litoral Sul (Peruíbe, Itanhaém, Mongaguá, Praia Grande, São Vicente) até Embu das Artes.

### Funcionalidades Principais

- Emissão de passagens com geração automática de PDF
- Cadastro e busca de clientes/passageiros
- Controle de motoristas e proprietários
- Registro de saídas de viagens
- Relatórios diários e por período
- Dashboard com métricas em tempo real
- Sistema de autenticação (Admin e Atendentes)

## Stack Tecnológica

### Backend
- **Python 3.10+**
- **FastAPI** - Framework web moderno e de alta performance
- **SQLAlchemy 2.0** - ORM para gerenciamento do banco de dados
- **SQLite** - Banco de dados relacional (production-ready)
- **JWT** - Autenticação via tokens Bearer
- **bcrypt** - Hashing seguro de senhas
- **ReportLab** - Geração de PDFs das passagens
- **Uvicorn** - Servidor ASGI com hot-reload

### Frontend
- **HTML5 + JavaScript Vanilla** - Sem frameworks, máxima performance
- **CSS Moderno** - Variáveis CSS, Grid, Flexbox
- **Plus Jakarta Sans** - Tipografia moderna
- **Lucide Icons** - Biblioteca de ícones SVG

### Deploy
- **Linux (Ubuntu 20.04+)** - Servidor recomendado
- **Nginx** - Reverse proxy e servidor de arquivos estáticos
- **Systemd** - Gerenciamento de serviços
- **Let's Encrypt** - Certificados SSL gratuitos
- **Alternativa:** Windows Server com IIS

## Estrutura do Projeto

```
APP EMBUIBE/
├── backend/
│   ├── app/
│   │   ├── models/          # Models SQLAlchemy (Cliente, Passagem, Viagem, etc)
│   │   ├── schemas/         # Schemas Pydantic (validação e serialização)
│   │   ├── routers/         # Endpoints da API por módulo
│   │   │   ├── auth.py      # Autenticação e login
│   │   │   ├── clientes.py  # CRUD de clientes
│   │   │   ├── passagens.py # Emissão de passagens
│   │   │   ├── viagens.py   # Registro de viagens
│   │   │   ├── relatorios.py # Relatórios diversos
│   │   │   └── dashboard.py # Métricas e resumos
│   │   ├── utils/           # Funções auxiliares
│   │   │   ├── security.py  # JWT, hash de senhas
│   │   │   └── pdf.py       # Geração de PDFs
│   │   ├── database.py      # Conexão SQLAlchemy
│   │   └── main.py          # Aplicação FastAPI principal
│   ├── requirements.txt     # Dependências Python
│   ├── create_tables.py     # Criação das tabelas
│   ├── seed_data.py         # População inicial do banco
│   └── expresso_embuibe.db  # Banco SQLite (gerado após seed)
├── frontend/
│   ├── pages/
│   │   ├── emissao.html     # Emissão de passagens
│   │   ├── clientes.html    # Gestão de clientes
│   │   ├── registro-saida.html # Registro de saídas
│   │   ├── relatorio.html   # Relatórios diários
│   │   └── admin/           # Páginas exclusivas admin
│   │       ├── dashboard.html  # Dashboard admin
│   │       └── relatorios.html # Relatórios avançados
│   ├── js/
│   │   └── api.js           # Cliente API (comunicação backend)
│   └── index.html           # Página de login
├── DEPLOY.md                # Guia completo de deploy
└── README.md                # Este arquivo
```

## Instalação

### Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno

### Passos para instalação

1. Clone o repositório ou faça download do projeto
```bash
git clone [url-do-repositorio]
cd "APP EMBUIBE"
```

2. Configure o Backend

```bash
# Navegar para pasta backend
cd backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

3. Inicializar o Banco de Dados

```bash
# Criar tabelas
python create_tables.py

# Popular dados iniciais (cidades, motoristas, usuários)
python seed_data.py
```

4. Configurar variáveis de ambiente (opcional para desenvolvimento)

Crie arquivo `.env` na pasta `backend`:
```env
SECRET_KEY=sua-chave-secreta-aqui-min-32-caracteres
DATABASE_URL=sqlite:///./expresso_embuibe.db
ENVIRONMENT=development
```

5. Iniciar o Backend

```bash
# Ainda na pasta backend com venv ativado
uvicorn app.main:app --reload --port 8000
```

6. Iniciar o Frontend (nova aba do terminal)

```bash
# Na pasta raiz do projeto
cd frontend
python -m http.server 3000
```

7. Acessar a aplicação

```
Frontend: http://localhost:3000
Backend API Docs: http://localhost:8000/docs
```

## Credenciais de Acesso Padrão

### Administrador
- **Login:** admin
- **Senha:** embuibe@2025

### Atendentes
- **Mariana**
  - Login: mariana
  - Senha: 2107

- **Daniela**
  - Login: daniela
  - Senha: 2106

**IMPORTANTE:** Altere as senhas padrão após o primeiro acesso!

## Uso da API

A documentação interativa da API está disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Principais Endpoints

- `POST /api/v1/auth/login` - Autenticação
- `GET /api/v1/clientes` - Listar clientes
- `POST /api/v1/passagens` - Emitir passagem
- `GET /api/v1/relatorios/diario` - Relatório do dia
- `POST /api/v1/viagens/registrar-saida` - Registrar saída

## Desenvolvimento

### Estrutura de Desenvolvimento por Fases

O projeto foi desenvolvido em 10 fases incrementais:

1. Setup Inicial e Configuração
2. Models do Banco de Dados
3. Seed de Dados Iniciais
4. Sistema de Autenticação (JWT)
5. CRUD de Clientes
6. Emissão de Passagens com PDF
7. Sistema de Relatórios
8. Registro de Viagens
9. Dashboard com Métricas
10. Endpoints Auxiliares

## Deploy em Produção

Para instruções completas de deploy em servidor Linux (Nginx) ou Windows Server (IIS), consulte o arquivo **[DEPLOY.md](DEPLOY.md)**.

O guia inclui:
- Configuração completa do servidor
- Setup do backend com Systemd/NSSM
- Configuração do Nginx como reverse proxy
- SSL com Let's Encrypt
- Backup automático do banco de dados
- Troubleshooting e manutenção

## Autor

**Otimizia (Matheus Prado)**

## Cliente

**Expresso Embuibe**

## Versão

1.0.0

## Data

09/12/2025

## Licença

Todos os direitos reservados - Expresso Embuibe
