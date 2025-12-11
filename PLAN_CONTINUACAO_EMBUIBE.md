# PLANO DE CONTINUAÇÃO - SISTEMA EXPRESSO EMBUIBE

## STATUS ATUAL
✅ Backend completo (10 fases concluídas)
✅ 40+ arquivos criados
✅ 35+ endpoints implementados
✅ 8 models SQLAlchemy
✅ Autenticação JWT
✅ Geração de PDF
✅ Sistema de relatórios

---

## PRÓXIMAS ETAPAS

### ETAPA 1: CONFIGURAÇÃO E TESTE DO BACKEND
**Prioridade: CRÍTICA**
**Tempo estimado: 30 minutos**

#### 1.1 Verificar e Criar arquivo .env
Crie o arquivo `.env` na raiz do projeto (se não existir) com:

```env
DATABASE_URL=sqlite:///./expresso_embuibe.db
SECRET_KEY=expresso-embuibe-secret-key-2025-muito-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

#### 1.2 Instalar Dependências
```bash
cd backend
pip install -r requirements.txt
```

#### 1.3 Criar as Tabelas no Banco
```python
# Criar arquivo: backend/create_tables.py
from app.database import engine, Base
from app.models import *

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

if __name__ == "__main__":
    create_tables()
```

Executar:
```bash
python create_tables.py
```

#### 1.4 Executar o Seed de Dados
```bash
python seed_data.py
```

Verificar se foram criados:
- 3 usuários (admin, mariana, daniela)
- 7 proprietários com motoristas
- 5 cidades
- 64 locais de embarque

#### 1.5 Iniciar o Servidor
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 1.6 Testar Endpoints Críticos

**Login (TESTAR PRIMEIRO):**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "senha": "embuibe@2025"}'
```

Deve retornar um token JWT.

**Listar Cidades:**
```bash
curl http://localhost:8000/api/v1/cidades \
  -H "Authorization: Bearer {TOKEN}"
```

**Listar Motoristas:**
```bash
curl http://localhost:8000/api/v1/motoristas \
  -H "Authorization: Bearer {TOKEN}"
```

#### 1.7 Acessar Documentação
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

### ETAPA 2: DESENVOLVIMENTO DO FRONTEND
**Prioridade: ALTA**
**Tempo estimado: 2-3 horas**

#### 2.1 Estrutura de Arquivos
Criar a seguinte estrutura em `frontend/`:

```
frontend/
├── index.html              # Página de login
├── pages/
│   ├── dashboard.html      # Dashboard atendente
│   ├── emissao.html        # Emissão de passagem
│   ├── clientes.html       # Cadastro/busca clientes
│   ├── relatorio.html      # Relatório diário
│   ├── registro-saida.html # Registro de saída
│   └── admin/
│       ├── dashboard.html  # Dashboard admin
│       └── relatorios.html # Relatórios com filtros
├── css/
│   └── styles.css          # Estilos customizados
├── js/
│   ├── api.js              # Cliente da API
│   ├── auth.js             # Autenticação
│   ├── utils.js            # Funções utilitárias
│   ├── dashboard.js        # Lógica do dashboard
│   ├── emissao.js          # Lógica de emissão
│   ├── clientes.js         # Lógica de clientes
│   ├── relatorio.js        # Lógica de relatórios
│   └── registro-saida.js   # Lógica de registro
└── assets/
    └── logo.png            # Logo (opcional)
```

#### 2.2 Arquivo Base - api.js
```javascript
// frontend/js/api.js
const API_URL = 'http://localhost:8000/api/v1';

class ApiClient {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${API_URL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (response.status === 401) {
                this.clearToken();
                window.location.href = '/index.html';
                return;
            }

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Erro na requisição');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth
    async login(login, senha) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ login, senha })
        });
        if (response.access_token) {
            this.setToken(response.access_token);
        }
        return response;
    }

    async getMe() {
        return this.request('/auth/me');
    }

    // Clientes
    async getClientes(query = '', page = 1, limit = 20) {
        return this.request(`/clientes?q=${query}&page=${page}&limit=${limit}`);
    }

    async createCliente(data) {
        return this.request('/clientes', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Cidades e Locais
    async getCidades() {
        return this.request('/cidades');
    }

    async getLocaisByCidade(cidadeId) {
        return this.request(`/cidades/${cidadeId}/locais`);
    }

    // Motoristas
    async getMotoristas() {
        return this.request('/motoristas');
    }

    // Passagens
    async emitirPassagem(data) {
        return this.request('/passagens', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Relatórios
    async getRelatorioDiario(data = null) {
        const param = data ? `?data=${data}` : '';
        return this.request(`/relatorios/diario${param}`);
    }

    async getRelatorioPeriodo(inicio, fim) {
        return this.request(`/relatorios/periodo?data_inicio=${inicio}&data_fim=${fim}`);
    }

    // Viagens
    async registrarSaida(data) {
        return this.request('/viagens/registrar-saida', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Dashboard
    async getDashboard() {
        return this.request('/dashboard/resumo');
    }
}

const api = new ApiClient();
```

#### 2.3 Página de Login - index.html
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Expresso Embuibe - Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gradient-to-br from-indigo-600 to-purple-700 min-h-screen flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <!-- Logo -->
        <div class="text-center mb-8">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-full mb-4">
                <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h8m-8 5h8m-4 5v-5m-8 5h16a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
            </div>
            <h1 class="text-2xl font-bold text-slate-800">Expresso Embuibe</h1>
            <p class="text-slate-500 mt-1">Sistema de Gestão de Passagens</p>
        </div>

        <!-- Formulário -->
        <form id="loginForm" class="space-y-5">
            <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">Usuário</label>
                <input 
                    type="text" 
                    id="login" 
                    name="login"
                    class="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
                    placeholder="Digite seu usuário"
                    required
                >
            </div>

            <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">Senha</label>
                <input 
                    type="password" 
                    id="senha" 
                    name="senha"
                    class="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
                    placeholder="Digite sua senha"
                    required
                >
            </div>

            <!-- Erro -->
            <div id="errorMsg" class="hidden bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm"></div>

            <button 
                type="submit" 
                id="btnLogin"
                class="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
            >
                <span>Entrar</span>
                <svg id="loadingIcon" class="hidden w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
            </button>
        </form>

        <p class="text-center text-slate-400 text-sm mt-6">
            © 2025 Expresso Embuibe - Desenvolvido por Otimizia
        </p>
    </div>

    <script src="js/api.js"></script>
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const login = document.getElementById('login').value;
            const senha = document.getElementById('senha').value;
            const btn = document.getElementById('btnLogin');
            const loading = document.getElementById('loadingIcon');
            const errorMsg = document.getElementById('errorMsg');

            // Loading state
            btn.disabled = true;
            loading.classList.remove('hidden');
            errorMsg.classList.add('hidden');

            try {
                const response = await api.login(login, senha);
                
                // Salvar dados do usuário
                localStorage.setItem('usuario', JSON.stringify(response.usuario));
                
                // Redirecionar baseado no tipo
                if (response.usuario.tipo === 'admin') {
                    window.location.href = '/pages/admin/dashboard.html';
                } else {
                    window.location.href = '/pages/dashboard.html';
                }
            } catch (error) {
                errorMsg.textContent = error.message || 'Usuário ou senha incorretos';
                errorMsg.classList.remove('hidden');
            } finally {
                btn.disabled = false;
                loading.classList.add('hidden');
            }
        });

        // Se já estiver logado, redirecionar
        if (localStorage.getItem('token')) {
            const usuario = JSON.parse(localStorage.getItem('usuario') || '{}');
            if (usuario.tipo === 'admin') {
                window.location.href = '/pages/admin/dashboard.html';
            } else {
                window.location.href = '/pages/dashboard.html';
            }
        }
    </script>
</body>
</html>
```

#### 2.4 Dashboard Atendente - pages/dashboard.html
Criar página com:
- Header com nome do usuário e logout
- Sidebar com menu de navegação
- Cards de métricas (viagens hoje, passageiros, faturamento)
- Lista de próximas saídas
- Botões de ação rápida

#### 2.5 Emissão de Passagem - pages/emissao.html
Criar página com:
- Busca de cliente (autocomplete)
- Botão "Novo Cliente" que abre modal
- Select de cidade
- Select de local de embarque (filtrado por cidade)
- Input de data e horário
- Select de motorista
- Radio buttons de forma de pagamento
- Preview da passagem
- Botão "Emitir"
- Modal de sucesso com botão "Enviar WhatsApp"

#### 2.6 Relatório Diário - pages/relatorio.html
Criar página com:
- Seletor de data
- Cards de resumo (passageiros, viagens, faturamento)
- Lista agrupada por horário
- Botão "Copiar Relatório"

#### 2.7 Registro de Saída - pages/registro-saida.html
Criar página com:
- Formulário: data, horário, motorista
- Botão "Buscar Passageiros"
- Lista de passageiros encontrados
- Resumo (total, valor)
- Botão "Confirmar Saída"

#### 2.8 Componente de Layout Reutilizável
Criar um template base com sidebar e header para reutilizar em todas as páginas.

---

### ETAPA 3: INTEGRAÇÃO FRONTEND + BACKEND
**Prioridade: ALTA**
**Tempo estimado: 1 hora**

#### 3.1 Configurar CORS no Backend
Verificar se o `main.py` tem CORS configurado:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 3.2 Servir Frontend pelo FastAPI
Adicionar ao `main.py`:

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Servir arquivos estáticos do frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Rota raiz serve o login
@app.get("/")
async def serve_frontend():
    return FileResponse("../frontend/index.html")
```

#### 3.3 Testar Fluxo Completo
1. Acessar http://localhost:8000
2. Fazer login com `mariana` / `2107`
3. Verificar se dashboard carrega
4. Testar emissão de passagem
5. Verificar PDF gerado
6. Testar relatório diário

---

### ETAPA 4: AJUSTES E CORREÇÕES
**Prioridade: MÉDIA**

#### 4.1 Tratamento de Erros
- Mensagens amigáveis para o usuário
- Log de erros no console
- Retry em falhas de conexão

#### 4.2 Validações no Frontend
- Campos obrigatórios
- Formato de telefone
- Data não pode ser passada
- Horário válido

#### 4.3 UX Improvements
- Loading states em todos os botões
- Feedback visual de sucesso/erro
- Confirmação antes de ações destrutivas
- Atalhos de teclado

---

### ETAPA 5: PREPARAR PARA DEPLOY
**Prioridade: MÉDIA**
**Tempo estimado: 1 hora**

#### 5.1 Criar Dockerfile (opcional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

WORKDIR /app/backend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 5.2 Configurar para Replit
Criar arquivo `replit.nix`:
```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.postgresql
  ];
}
```

Criar arquivo `.replit`:
```
run = "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000"
language = "python3"

[nix]
channel = "stable-23_05"
```

#### 5.3 Variáveis de Ambiente para Produção
```env
DATABASE_URL=postgresql://user:pass@host:5432/expresso_embuibe
SECRET_KEY=chave-muito-segura-para-producao-mudar-isso
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

---

## CHECKLIST FINAL

```
BACKEND
□ Servidor iniciando sem erros
□ Seed executado com sucesso
□ Login funcionando (todos os usuários)
□ Endpoints retornando dados corretos
□ PDF sendo gerado corretamente
□ Documentação acessível (/docs)

FRONTEND
□ Login funcionando
□ Redirecionamento por tipo de usuário
□ Dashboard carregando métricas
□ Emissão de passagem completa
□ PDF disponível para download/WhatsApp
□ Relatório diário funcionando
□ Registro de saída funcionando
□ Logout funcionando

INTEGRAÇÃO
□ CORS configurado
□ Token sendo enviado em todas as requisições
□ Erros sendo tratados
□ Responsivo em tablet

SEGURANÇA
□ Senhas com hash
□ Tokens expirando
□ Rotas protegidas
□ Validação de inputs
```

---

## COMANDOS ÚTEIS

```bash
# Iniciar backend
cd backend
uvicorn app.main:app --reload

# Recriar banco de dados
rm expresso_embuibe.db
python create_tables.py
python seed_data.py

# Ver logs
uvicorn app.main:app --reload --log-level debug

# Testar endpoint específico
curl -X GET http://localhost:8000/api/v1/cidades -H "Authorization: Bearer {TOKEN}"
```

---

## ORDEM DE EXECUÇÃO

1. **PRIMEIRO**: Verificar .env e instalar dependências
2. **SEGUNDO**: Criar tabelas e executar seed
3. **TERCEIRO**: Iniciar servidor e testar endpoints
4. **QUARTO**: Criar frontend página por página
5. **QUINTO**: Integrar e testar fluxo completo
6. **SEXTO**: Ajustes e correções
7. **SÉTIMO**: Deploy no Replit

---

## INÍCIO

Comece pela ETAPA 1 - verificando se o arquivo .env existe e se as dependências estão instaladas. Depois crie as tabelas e execute o seed para popular o banco com os dados iniciais.
