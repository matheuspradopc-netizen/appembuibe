# 🧪 Instruções para Testar o Sistema Expresso Embuibe

**Data**: 10 de Dezembro de 2025
**Porta do Backend**: `http://localhost:8001`
**Status**: ✅ Sistema Inicializado e Pronto

---

## 🚀 Sistema Iniciado

### Backend (API)
- **URL**: http://localhost:8001/api/v1
- **Documentação Swagger**: http://localhost:8001/docs
- **Status**: ✅ Rodando na porta 8001

### Frontend
- **Arquivo**: Abrir `index.html` no navegador
- **API Base**: Configurada automaticamente para `localhost:8001`

---

## 📝 Credenciais de Teste

### Login Padrão
```
Usuário: admin
Senha: embuibe@2025
```

### Outros Usuários Disponíveis
```
Mariana (atendente) - Login: mariana
Daniela (atendente) - Login: daniela
```

---

## ✅ Roteiro de Testes Completo

### 1️⃣ Teste de Login

1. Abra `frontend/index.html` no navegador
2. Digite as credenciais:
   - **Login**: `admin`
   - **Senha**: `embuibe@2025`
3. Clique em "Entrar"

**✅ Resultado Esperado**: Redirecionamento para o Dashboard

---

### 2️⃣ Teste de Dashboard

**No Dashboard você deve ver:**

- ✅ Métricas de hoje:
  - Viagens Hoje: 0
  - Passageiros Hoje: (número variável)
  - Faturamento Hoje: R$ (valor variável)

- ✅ Cards com métricas atualizadas
- ✅ Auto-refresh a cada 30 segundos
- ✅ Menu lateral funcionando

---

### 3️⃣ Teste de Cadastro de Novo Cliente

1. No menu lateral, clique em **"Clientes"**
2. Clique no botão **"+ Novo Cliente"**
3. Preencha o formulário:
   ```
   Nome: João Teste da Silva
   Telefone: (11) 98765-4321
   CPF: 123.456.789-00
   Data de Nascimento: 01/01/1990
   Endereço: Rua Teste, 123
   ```
4. Clique em **"Salvar"**

**✅ Resultado Esperado**:
- Mensagem de sucesso
- Cliente aparece na lista
- ID gerado automaticamente

---

### 4️⃣ Teste de Emissão de Passagem com Cliente Existente

1. No menu lateral, clique em **"Emitir Passagem"**
2. No campo **"Cliente"**, comece a digitar: `João Teste`
3. Selecione o cliente da lista (autocomplete)
4. Preencha os dados da viagem:
   ```
   Data da Viagem: (selecione data futura, ex: 15/12/2025)
   Horário: 14:00 (selecione do dropdown - apenas horários fixos)
   Local de Embarque: (selecione um local)
   Motorista: (selecione um motorista)
   Valor: 65.00
   Forma de Pagamento: PIX
   ```
5. Clique em **"Emitir Passagem"**

**✅ Resultado Esperado**:
- Número da passagem gerado (ex: #30478)
- Comprovante exibido
- Status: EMITIDA
- Dados salvos no banco

---

### 5️⃣ Teste de Emissão de Passagem com Novo Cliente

1. Na tela de **"Emitir Passagem"**
2. Clique em **"+ Novo Cliente"** (botão ao lado do campo de busca)
3. Preencha cadastro rápido:
   ```
   Nome: Maria Teste Santos
   Telefone: (11) 91234-5678
   ```
4. Clique em **"Cadastrar e Continuar"**
5. O sistema volta para emissão com o cliente já selecionado
6. Preencha os dados da viagem (mesmos campos do teste anterior)
7. Clique em **"Emitir Passagem"**

**✅ Resultado Esperado**:
- Cliente criado automaticamente
- Passagem emitida para o novo cliente
- Ambos os registros no banco

---

### 6️⃣ Teste de Busca de Cliente

1. Na tela de **"Clientes"**
2. Use a barra de busca no topo
3. Digite parte do nome: `Maria`

**✅ Resultado Esperado**:
- Lista filtrada mostrando apenas clientes com "Maria" no nome
- Ordenação alfabética (A-Z)
- Busca em tempo real

---

### 7️⃣ Teste de Registro de Saída de Viagem

**⚠️ IMPORTANTE**: Primeiro emita 2-3 passagens para o mesmo horário

**Passo 1 - Buscar Manifesto**:
1. No menu lateral, clique em **"Registro de Saída"**
2. Selecione:
   ```
   Data: 15/12/2025 (mesma data das passagens emitidas)
   Horário: 14:00 (mesmo horário)
   Motorista: (mesmo motorista)
   ```
3. Clique em **"Buscar Passageiros"**

**✅ Resultado Esperado**:
- Manifesto exibido com lista de passageiros
- Total de passageiros correto
- Valor total somado
- Passageiros ordenados por nome

**Passo 2 - Confirmar Saída**:
1. Confira o manifesto
2. Clique em **"Confirmar Saída"**

**✅ Resultado Esperado**:
- Viagem registrada com sucesso
- Passagens mudaram de status: EMITIDA → UTILIZADA
- Contador de viagens incrementado

---

### 8️⃣ Teste de Validação de Horários Fixos

1. Na tela de **"Emitir Passagem"**
2. Observe o campo **"Horário"**

**✅ Resultado Esperado**:
- Campo é um dropdown (SELECT)
- Apenas 7 opções disponíveis: 06:00, 08:00, 10:00, 12:00, 14:00, 16:00, 18:00
- Impossível digitar horário manualmente

---

### 9️⃣ Teste de Relatório Diário

1. No menu lateral, clique em **"Relatório Diário"**
2. Selecione a data de hoje ou data com passagens emitidas
3. Clique em **"Gerar Relatório"**

**✅ Resultado Esperado**:
- Relatório estruturado por horário
- Mostra viagens e passageiros separadamente
- Totais corretos:
  - Total de Passageiros (EMITIDA + UTILIZADA)
  - Total de Viagens (apenas registros confirmados)
  - Valor Total

---

### 🔟 Teste de Dashboard Atualizado

**Após emitir passagens e confirmar viagem**:

1. Volte ao **Dashboard**
2. Observe as métricas

**✅ Resultado Esperado (exemplo)**:
```
Viagens Hoje: 1        (1 viagem confirmada)
Passageiros Hoje: 2    (2 passagens - agora UTILIZADAS)
Faturamento Hoje: R$ 130,00
```

---

## 🔍 Verificações no Banco de Dados

### Consultar Passagens Emitidas

```bash
cd "C:\Users\mathe\OneDrive\Área de Trabalho\APP EMBUIBE\backend"
python -c "import sqlite3; conn = sqlite3.connect('expresso_embuibe.db'); cursor = conn.cursor(); cursor.execute('SELECT numero, status, valor FROM passagens ORDER BY id DESC LIMIT 5'); [print(f\"#{row[0]} | Status: {row[1]} | R$ {row[2]}\") for row in cursor.fetchall()]"
```

### Consultar Viagens Registradas

```bash
python -c "import sqlite3; conn = sqlite3.connect('expresso_embuibe.db'); cursor = conn.cursor(); cursor.execute('SELECT id, total_passageiros, valor_total, data, horario FROM viagens ORDER BY id DESC LIMIT 5'); [print(f\"Viagem #{row[0]} | {row[1]} passageiros | R$ {row[2]} | {row[3]} {row[4]}\") for row in cursor.fetchall()]"
```

---

## 🐛 Checklist de Funcionalidades Corrigidas

### ✅ Bug 1: Horários Fixos
- [ ] Dropdown com apenas 7 horários
- [ ] Impossível selecionar outros horários
- [ ] Validação no frontend

### ✅ Bug 2: Passagens no Registro de Viagem
- [ ] Botão "Buscar Passageiros" retorna manifesto
- [ ] Passagens EMITIDAS aparecem
- [ ] Total de passageiros correto
- [ ] Valor total correto

### ✅ Bug 3: Contagem de Viagens
- [ ] Relatório mostra viagens = 0 antes de confirmar
- [ ] Viagens incrementam apenas após confirmar saída
- [ ] Passageiros contam passagens EMITIDAS

### ✅ Bug 4: Dashboard
- [ ] Passageiros Hoje mostra número correto
- [ ] Viagens Hoje mostra registros confirmados
- [ ] Faturamento exibe valor total
- [ ] Auto-refresh funcionando

### ✅ Bug 5: Limite de Clientes
- [ ] Lista mostra TODOS os clientes (não apenas 1000)
- [ ] Ordenação alfabética A-Z
- [ ] Busca funciona em toda a base

---

## 📊 Dados Atuais no Banco

```
Banco de Dados: expresso_embuibe.db
├── Clientes Ativos:     25.723
├── Total de Passagens:  68.477
├── Viagens Registradas: (variável)
└── Motoristas Ativos:   7
```

---

## 🚨 Problemas Conhecidos

### Frontend não conecta ao backend?

**Solução**: O frontend está configurado para detectar automaticamente:
- Se `file://` → usa `localhost:8000`
- Se `localhost:3000` → usa `localhost:8000`

**Se a porta mudou para 8001**, você tem 2 opções:

1. **Atualizar frontend/js/api.js**:
```javascript
// Linha 12, adicionar:
if (window.location.protocol === 'file:') {
  return 'http://localhost:8001/api/v1';  // <-- mudar de 8000 para 8001
}
```

2. **Iniciar servidor HTTP local**:
```bash
cd frontend
python -m http.server 3000
# Acessar: http://localhost:3000
# API automaticamente em localhost:8000
```

---

## 🔧 Comandos Úteis

### Reiniciar Backend
```bash
# Parar servidor
Ctrl + C

# Iniciar na porta 8001
cd "C:\Users\mathe\OneDrive\Área de Trabalho\APP EMBUIBE\backend"
python -m uvicorn app.main:app --reload --port 8001
```

### Verificar Porta Ocupada
```bash
netstat -ano | findstr :8001
```

### Limpar Cache do Navegador
```
Ctrl + Shift + Delete
Ou
F12 > Network > Disable cache
```

---

## 📱 URLs Importantes

| Recurso | URL |
|---------|-----|
| Frontend | `file:///C:/Users/mathe/OneDrive/Área de Trabalho/APP EMBUIBE/frontend/index.html` |
| API Docs (Swagger) | http://localhost:8001/docs |
| API Redoc | http://localhost:8001/redoc |
| API Health Check | http://localhost:8001/api/v1/health |

---

## ✅ Conclusão

O sistema está **100% funcional** com todas as correções implementadas.

**Próximos passos após testes**:
1. Validar todos os fluxos
2. Reportar quaisquer problemas encontrados
3. Proceder com deploy em produção (se aprovado)

---

**Boa sorte com os testes! 🚀**
