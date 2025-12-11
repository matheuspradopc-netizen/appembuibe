/**
 * API Client - Expresso Embuibe
 * Cliente para comunicação com o backend
 */

// Configuração da URL da API
// Em desenvolvimento: usa localhost:8000
// Em produção: usa o mesmo host que o frontend
const getApiBaseUrl = () => {
  // Se está em file:// (desenvolvimento local com arquivos), usa localhost
  if (window.location.protocol === 'file:') {
    return 'http://localhost:8000/api/v1';
  }

  // Se tem variável de ambiente configurada (para builds)
  if (typeof API_URL !== 'undefined') {
    return API_URL;
  }

  // Em desenvolvimento (porta 3000), usa o mesmo host mas porta 8000 do backend
  // Isso permite testar tanto em localhost quanto pelo IP da rede local (celular)
  if (window.location.port === '3000') {
    return `http://${window.location.hostname}:8000/api/v1`;
  }

  // Em produção, usa URL relativa (mesmo domínio do frontend)
  // Assume que backend está servindo em /api/v1 no mesmo servidor
  return '/api/v1';
};

const API_BASE_URL = getApiBaseUrl();

/**
 * Cliente HTTP com gerenciamento de autenticação
 */
class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  /**
   * Obtém o token do localStorage
   */
  getToken() {
    return localStorage.getItem('token');
  }

  /**
   * Define o token no localStorage
   */
  setToken(token) {
    localStorage.setItem('token', token);
  }

  /**
   * Remove o token do localStorage
   */
  removeToken() {
    localStorage.removeItem('token');
  }

  /**
   * Obtém os headers padrão da requisição
   */
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (includeAuth) {
      const token = this.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  /**
   * Faz uma requisição HTTP
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(options.auth !== false),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      // Se não autorizado, redireciona para login
      if (response.status === 401) {
        this.removeToken();
        if (window.location.pathname !== '/index.html' && window.location.pathname !== '/') {
          window.location.href = '/index.html';
        }
        throw new Error('Não autorizado');
      }

      // Se não encontrado
      if (response.status === 404) {
        throw new Error('Recurso não encontrado');
      }

      // Se erro de servidor
      if (response.status >= 500) {
        throw new Error('Erro no servidor. Tente novamente mais tarde.');
      }

      // Tenta parsear JSON
      const data = await response.json().catch(() => null);

      if (!response.ok) {
        // Extrai mensagem de erro legível
        let errorMessage = 'Erro na requisição';
        if (data?.detail) {
          if (typeof data.detail === 'string') {
            errorMessage = data.detail;
          } else if (Array.isArray(data.detail)) {
            // Erros de validação do Pydantic
            errorMessage = data.detail.map(e => e.msg || e.message || String(e)).join(', ');
          }
        } else if (data?.message) {
          errorMessage = data.message;
        }
        throw new Error(errorMessage);
      }

      return data;
    } catch (error) {
      if (error.message === 'Failed to fetch') {
        throw new Error('Erro de conexão. Verifique sua internet ou se o servidor está rodando.');
      }
      throw error;
    }
  }

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  /**
   * POST request
   */
  async post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * PUT request
   */
  async put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }
}

/**
 * API Service - Métodos específicos para cada endpoint
 */
class ApiService {
  constructor() {
    this.client = new ApiClient(API_BASE_URL);
  }

  // ==================== AUTH ====================

  /**
   * Faz login
   */
  async login(login, senha) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ login, senha }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Erro ao fazer login');
    }

    const data = await response.json();
    this.client.setToken(data.access_token);
    return data;
  }

  /**
   * Obtém dados do usuário atual
   */
  async getMe() {
    return this.client.get('/auth/me');
  }

  /**
   * Faz logout
   */
  logout() {
    this.client.removeToken();
    window.location.href = '/index.html';
  }

  // ==================== CLIENTES ====================

  /**
   * Lista clientes com busca e paginação
   */
  async getClientes(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.client.get(`/clientes?${queryString}`);
  }

  /**
   * Busca cliente por ID
   */
  async getCliente(id) {
    return this.client.get(`/clientes/${id}`);
  }

  /**
   * Cria novo cliente
   */
  async createCliente(data) {
    return this.client.post('/clientes', data);
  }

  /**
   * Atualiza cliente
   */
  async updateCliente(id, data) {
    return this.client.put(`/clientes/${id}`, data);
  }

  /**
   * Remove cliente (soft delete)
   */
  async deleteCliente(id) {
    return this.client.delete(`/clientes/${id}`);
  }

  // ==================== CIDADES E LOCAIS ====================

  /**
   * Lista todas as cidades
   */
  async getCidades() {
    return this.client.get('/cidades');
  }

  /**
   * Lista locais de embarque de uma cidade
   */
  async getLocaisByCidade(cidadeId) {
    return this.client.get(`/cidades/${cidadeId}/locais`);
  }

  /**
   * Lista todos os locais de embarque
   */
  async getLocaisEmbarque() {
    return this.client.get('/locais-embarque');
  }

  // ==================== MOTORISTAS ====================

  /**
   * Lista todos os motoristas
   */
  async getMotoristas() {
    return this.client.get('/motoristas');
  }

  // ==================== PASSAGENS ====================

  /**
   * Emite uma nova passagem
   */
  async emitirPassagem(data) {
    return this.client.post('/passagens', data);
  }

  /**
   * Busca passagem por ID
   */
  async getPassagem(id) {
    return this.client.get(`/passagens/${id}`);
  }

  /**
   * Obtém PDF de uma passagem
   */
  async getPassagemPDF(id) {
    return this.client.get(`/passagens/${id}/pdf`);
  }

  /**
   * Lista passagens de um dia
   */
  async getPassagensDia(data) {
    return this.client.get(`/passagens/dia/${data}`);
  }

  // ==================== VIAGENS ====================

  /**
   * Busca manifesto de passageiros ANTES de registrar saída
   */
  async buscarManifesto(data) {
    return this.client.post('/viagens/buscar-manifesto', data);
  }

  /**
   * Registra saída de viagem
   */
  async registrarSaida(data) {
    return this.client.post('/viagens/registrar-saida', data);
  }

  /**
   * Lista viagens
   */
  async getViagens(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.client.get(`/viagens/listar?${queryString}`);
  }

  /**
   * Obtém manifesto de uma viagem
   */
  async getManifesto(viagemId) {
    return this.client.get(`/viagens/${viagemId}/manifesto`);
  }

  // ==================== RELATÓRIOS ====================

  /**
   * Relatório diário
   */
  async getRelatorioDiario(data) {
    return this.client.get(`/relatorios/diario?data=${data}`);
  }

  /**
   * Relatório por período
   */
  async getRelatorioPeriodo(dataInicio, dataFim) {
    return this.client.get(`/relatorios/periodo?data_inicio=${dataInicio}&data_fim=${dataFim}`);
  }

  /**
   * Relatório por motorista
   */
  async getRelatorioMotorista(motoristaId, dataInicio, dataFim) {
    return this.client.get(`/relatorios/motorista/${motoristaId}?data_inicio=${dataInicio}&data_fim=${dataFim}`);
  }

  // ==================== DASHBOARD ====================

  /**
   * Obtém resumo do dashboard
   */
  async getDashboardResumo() {
    return this.client.get('/dashboard/resumo');
  }

  /**
   * Obtém métricas rápidas
   */
  async getMetricasRapidas() {
    return this.client.get('/dashboard/metricas-rapidas');
  }
}

// Instância global da API
const api = new ApiService();

// Exporta para uso global
if (typeof window !== 'undefined') {
  window.api = api;
}
