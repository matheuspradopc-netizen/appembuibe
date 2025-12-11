# PLANO FRONTEND - EXPRESSO EMBUIBE
## Design de Alta Qualidade

---

## SKILL: FRONTEND-DESIGN (INSTRUÇÕES OBRIGATÓRIAS)

Esta skill guia a criação de interfaces frontend distintivas e de qualidade profissional que evitam a estética genérica de "IA". Implemente código real e funcional com atenção excepcional aos detalhes estéticos e escolhas criativas.

### Design Thinking

Antes de codar, entenda o contexto e comprometa-se com uma direção estética BOLD:

- **Propósito**: Sistema de gestão de transporte de passageiros. Usado por atendentes e proprietários.
- **Tom**: Clean, Professional, Confiável, Moderno
- **Diferenciação**: Clareza nas informações, ações rápidas, visual que transmite organização

### Diretrizes de Estética Frontend

Foque em:

1. **Tipografia**: Escolha fontes bonitas, únicas e interessantes. EVITE fontes genéricas como Arial, Inter, Roboto. Opte por escolhas distintivas que elevam a estética. Combine uma fonte display característica com uma fonte body refinada.

2. **Cor & Tema**: Comprometa-se com uma estética coesa. Use CSS variables para consistência. Cores dominantes com acentos fortes superam paletas tímidas e distribuídas igualmente.

3. **Motion**: Use animações para efeitos e micro-interações. Priorize soluções CSS-only. Foque em momentos de alto impacto: uma carga de página bem orquestrada com reveals escalonados (animation-delay) cria mais prazer que micro-interações espalhadas. Use scroll-triggering e hover states que surpreendem.

4. **Composição Espacial**: Layouts inesperados. Assimetria. Sobreposição. Fluxo diagonal. Elementos que quebram o grid. Espaço negativo generoso OU densidade controlada.

5. **Backgrounds & Detalhes Visuais**: Crie atmosfera e profundidade em vez de defaultar para cores sólidas. Adicione efeitos e texturas contextuais que combinam com a estética geral.

### O QUE NUNCA FAZER:

- ❌ Fontes genéricas (Inter, Roboto, Arial, system fonts)
- ❌ Esquemas de cor clichê (gradientes roxos em fundo branco)
- ❌ Layouts previsíveis e padrões de componentes
- ❌ Design cookie-cutter sem caráter específico ao contexto
- ❌ Convergir para escolhas comuns entre gerações

### IMPORTANTE:

Combine complexidade de implementação com a visão estética. Designs minimalistas ou refinados precisam de restrição, precisão e atenção cuidadosa a espaçamento, tipografia e detalhes sutis. Elegância vem de executar bem a visão.

---

## CONTEXTO DO PROJETO

### O que é:
Sistema web para empresa de transporte de passageiros (vans) que opera na rota Peruíbe → Embu das Artes.

### Usuários:
- **Atendentes** (Mariana, Daniela): Emitem passagens, cadastram clientes, geram relatórios
- **Admin/Proprietários**: Visualizam dashboards, relatórios financeiros, métricas

### Funcionalidades:
1. Login com autenticação JWT
2. Emissão de passagem com geração de PDF
3. Cadastro de clientes
4. Relatório diário por horário
5. Registro de saída de viagem
6. Dashboard com métricas em tempo real

---

## REFERÊNCIAS VISUAIS

As imagens de referência na pasta mostram:
- Sidebar fixa à esquerda com menu de navegação
- Cards brancos com sombras suaves
- Métricas em destaque com números grandes
- Gráficos de linha suaves
- Tabelas minimalistas
- Fundo cinza claro (#F8FAFC)
- Paleta predominantemente azul/indigo

**SIGA O LAYOUT E ESTRUTURA DAS REFERÊNCIAS, MAS APLIQUE OS PRINCÍPIOS DA SKILL PARA TORNAR ÚNICO.**

---

## DESIGN SYSTEM

### Tipografia

```html
<!-- Fonte Principal - Plus Jakarta Sans (moderna, geométrica, profissional) -->
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<!-- Alternativa - Outfit (clean, contemporânea) -->
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
```

```css
body {
  font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Hierarquia */
.text-display { font-size: 3rem; font-weight: 800; letter-spacing: -0.02em; }
.text-h1 { font-size: 1.875rem; font-weight: 700; letter-spacing: -0.01em; }
.text-h2 { font-size: 1.5rem; font-weight: 600; }
.text-h3 { font-size: 1.25rem; font-weight: 600; }
.text-body { font-size: 1rem; font-weight: 400; }
.text-small { font-size: 0.875rem; font-weight: 400; }
.text-tiny { font-size: 0.75rem; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; }
```

### Cores

```css
:root {
  /* Background */
  --bg-page: #F8FAFC;
  --bg-card: #FFFFFF;
  --bg-sidebar: #FFFFFF;
  --bg-hover: #F1F5F9;
  
  /* Primary - Indigo */
  --primary-50: #EEF2FF;
  --primary-100: #E0E7FF;
  --primary-500: #6366F1;
  --primary-600: #4F46E5;
  --primary-700: #4338CA;
  
  /* Success - Emerald */
  --success-50: #ECFDF5;
  --success-500: #10B981;
  --success-600: #059669;
  
  /* Warning - Amber */
  --warning-50: #FFFBEB;
  --warning-500: #F59E0B;
  
  /* Error - Red */
  --error-50: #FEF2F2;
  --error-500: #EF4444;
  
  /* Neutral */
  --slate-50: #F8FAFC;
  --slate-100: #F1F5F9;
  --slate-200: #E2E8F0;
  --slate-300: #CBD5E1;
  --slate-400: #94A3B8;
  --slate-500: #64748B;
  --slate-600: #475569;
  --slate-700: #334155;
  --slate-800: #1E293B;
  --slate-900: #0F172A;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  
  /* Border Radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-2xl: 1.5rem;
  --radius-full: 9999px;
}
```

### Componentes

#### Card Base
```css
.card {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--slate-100);
  padding: 1.5rem;
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
```

#### Card de Métrica
```html
<div class="metric-card">
  <div class="metric-icon" style="--icon-color: var(--primary-500); --icon-bg: var(--primary-50);">
    <i data-lucide="users"></i>
  </div>
  <div class="metric-content">
    <span class="metric-label">PASSAGEIROS HOJE</span>
    <span class="metric-value">127</span>
    <span class="metric-trend positive">
      <i data-lucide="trending-up"></i>
      +12% vs ontem
    </span>
  </div>
</div>
```

```css
.metric-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--slate-100);
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  background: var(--icon-bg);
  color: var(--icon-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-icon svg {
  width: 24px;
  height: 24px;
}

.metric-label {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--slate-500);
}

.metric-value {
  font-size: 2rem;
  font-weight: 800;
  color: var(--slate-800);
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.metric-trend {
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.metric-trend.positive { color: var(--success-500); }
.metric-trend.negative { color: var(--error-500); }
```

#### Botões
```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: var(--radius-lg);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: var(--primary-600);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-700);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background: white;
  color: var(--slate-700);
  border: 1px solid var(--slate-200);
}

.btn-secondary:hover {
  background: var(--slate-50);
  border-color: var(--slate-300);
}

.btn-success {
  background: var(--success-500);
  color: white;
}

.btn-success:hover {
  background: var(--success-600);
}

/* Loading State */
.btn-loading {
  position: relative;
  color: transparent !important;
  pointer-events: none;
}

.btn-loading::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

#### Inputs
```css
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--slate-700);
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 1px solid var(--slate-200);
  border-radius: var(--radius-lg);
  background: white;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px var(--primary-50);
}

.form-input::placeholder {
  color: var(--slate-400);
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1rem;
  padding-right: 2.5rem;
}
```

#### Tabela
```css
.table-container {
  overflow-x: auto;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--slate-100);
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table thead {
  background: var(--slate-50);
}

.table th {
  padding: 0.875rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--slate-500);
  text-align: left;
  border-bottom: 1px solid var(--slate-200);
}

.table td {
  padding: 1rem;
  font-size: 0.875rem;
  color: var(--slate-700);
  border-bottom: 1px solid var(--slate-100);
}

.table tbody tr {
  transition: background 0.15s ease;
}

.table tbody tr:hover {
  background: var(--slate-50);
}

.table tbody tr:last-child td {
  border-bottom: none;
}
```

#### Badges
```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: var(--radius-full);
}

.badge-success {
  background: var(--success-50);
  color: var(--success-600);
}

.badge-warning {
  background: var(--warning-50);
  color: var(--warning-500);
}

.badge-error {
  background: var(--error-50);
  color: var(--error-500);
}

.badge-info {
  background: var(--primary-50);
  color: var(--primary-600);
}
```

### Layout

#### Sidebar
```css
.layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 260px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--slate-200);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 50;
}

.sidebar-logo {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-bottom: 1px solid var(--slate-100);
}

.sidebar-logo-icon {
  width: 40px;
  height: 40px;
  background: var(--primary-600);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.sidebar-logo-text {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--slate-800);
}

.sidebar-menu {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  color: var(--slate-600);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.15s ease;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background: var(--slate-50);
  color: var(--slate-800);
}

.menu-item.active {
  background: var(--primary-50);
  color: var(--primary-600);
  border-left-color: var(--primary-600);
}

.menu-item svg {
  width: 20px;
  height: 20px;
}

.sidebar-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--slate-100);
}
```

#### Main Content
```css
.main {
  flex: 1;
  margin-left: 260px;
  background: var(--bg-page);
  min-height: 100vh;
}

.header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--slate-200);
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 40;
}

.content {
  padding: 2rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--slate-800);
  margin-bottom: 1.5rem;
}

.grid-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}
```

### Animações

```css
/* Fade In */
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide Up */
.animate-slide-up {
  animation: slideUp 0.4s ease-out forwards;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Stagger - usar com animation-delay */
.stagger-1 { animation-delay: 0.1s; }
.stagger-2 { animation-delay: 0.2s; }
.stagger-3 { animation-delay: 0.3s; }
.stagger-4 { animation-delay: 0.4s; }

/* Scale In */
.animate-scale-in {
  animation: scaleIn 0.3s ease-out forwards;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```

---

## ÍCONES

Usar Lucide Icons:

```html
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
<script>lucide.createIcons();</script>

<!-- Uso -->
<i data-lucide="bus"></i>
<i data-lucide="users"></i>
<i data-lucide="ticket"></i>
<i data-lucide="file-text"></i>
<i data-lucide="dollar-sign"></i>
<i data-lucide="calendar"></i>
<i data-lucide="search"></i>
<i data-lucide="plus"></i>
<i data-lucide="log-out"></i>
<i data-lucide="chevron-down"></i>
<i data-lucide="check-circle"></i>
<i data-lucide="x-circle"></i>
<i data-lucide="trending-up"></i>
<i data-lucide="trending-down"></i>
```

---

## TELAS A CRIAR

### 1. Login (`index.html`)
- Fundo: Gradiente indigo-purple ou padrão geométrico sutil
- Card centralizado branco com border-radius grande
- Logo + título do sistema
- Inputs estilizados com ícones
- Botão primário com hover
- Estado de loading
- Mensagem de erro animada

### 2. Dashboard Atendente (`pages/dashboard.html`)
- Sidebar com menu
- Header com saudação + usuário + logout
- Grid de 3 métricas: Viagens Hoje, Passageiros, Faturamento
- Seção "Próximas Saídas" (tabela)
- Seção "Últimas Passagens" (lista compacta)
- Botões de ação rápida

### 3. Emissão de Passagem (`pages/emissao.html`)
- Layout 2 colunas: Form (60%) + Preview (40%)
- Steps visuais numerados
- Busca cliente com autocomplete
- Modal novo cliente
- Selects encadeados (cidade → local)
- Preview estilo ticket
- Modal sucesso com botão WhatsApp

### 4. Clientes (`pages/clientes.html`)
- Busca proeminente
- Botão novo cliente
- Tabela paginada
- Ações por linha

### 5. Relatório Diário (`pages/relatorio.html`)
- Date picker
- Cards resumo
- Lista agrupada por horário
- Botão copiar

### 6. Registro de Saída (`pages/registro-saida.html`)
- Form compacto
- Lista de passageiros (manifesto)
- Resumo destacado
- Confirmação

### 7. Dashboard Admin (`pages/admin/dashboard.html`)
- Métricas expandidas
- Gráfico de linha (se possível com Chart.js)
- Distribuição por cidade
- Últimas viagens

### 8. Relatórios Admin (`pages/admin/relatorios.html`)
- Filtros avançados
- Tabela completa
- Totalizadores

---

## ESTRUTURA DE ARQUIVOS

```
frontend/
├── index.html                 # Login
├── pages/
│   ├── dashboard.html
│   ├── emissao.html
│   ├── clientes.html
│   ├── relatorio.html
│   ├── registro-saida.html
│   └── admin/
│       ├── dashboard.html
│       └── relatorios.html
├── css/
│   └── styles.css             # Todos os estilos (usar o CSS deste plano)
├── js/
│   ├── api.js                 # Cliente API
│   ├── auth.js                # Autenticação
│   ├── utils.js               # Helpers
│   └── [pagina].js            # Lógica específica
└── assets/
    └── (imagens se necessário)
```

---

## API

```javascript
const API_URL = 'http://localhost:8000/api/v1';

// Endpoints principais:
// POST /auth/login
// GET /auth/me
// GET /clientes?q=&page=&limit=
// POST /clientes
// GET /cidades
// GET /cidades/{id}/locais
// GET /motoristas
// POST /passagens
// GET /relatorios/diario?data=
// POST /viagens/registrar-saida
// GET /dashboard/resumo
```

---

## ORDEM DE EXECUÇÃO

1. Criar `frontend/css/styles.css` com todo o CSS deste plano
2. Criar `frontend/js/api.js` com cliente da API
3. Criar `frontend/index.html` (login) - TESTAR LOGIN
4. Criar layout base (sidebar + header)
5. Criar `pages/dashboard.html`
6. Criar `pages/emissao.html` (mais complexa)
7. Criar demais páginas

---

## CHECKLIST DE QUALIDADE

Cada página deve ter:
- [ ] Animações de entrada (fade-in, slide-up)
- [ ] Hover states em todos elementos clicáveis
- [ ] Focus states visíveis nos inputs
- [ ] Loading states nos botões
- [ ] Mensagens de erro/sucesso
- [ ] Tipografia consistente
- [ ] Espaçamento generoso
- [ ] Responsivo em tablet (min 768px)

---

## INÍCIO

Comece criando o arquivo CSS com todas as variáveis e componentes base. Depois crie a página de login completa e funcional. Teste o login com a API antes de prosseguir para as outras páginas.

Lembre-se: **QUALIDADE > VELOCIDADE**. Cada tela deve parecer feita por um designer profissional.
