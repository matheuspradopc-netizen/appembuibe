# Guia de Deploy - Expresso Embuibe

Sistema completo de gestão de transporte de passageiros.

---

## 📋 Pré-requisitos

### Servidor
- Sistema operacional: Linux (Ubuntu 20.04+ recomendado) ou Windows Server
- Python 3.10 ou superior
- Nginx ou Apache (para servir frontend e fazer proxy)
- Acesso SSH ao servidor
- Domínio configurado (opcional mas recomendado)

### Ferramentas
- Git
- pip (gerenciador de pacotes Python)
- venv (ambiente virtual Python)

---

## 🚀 Deploy em Produção

### 1. Preparação do Servidor

```bash
# Atualizar sistema (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install python3 python3-pip python3-venv nginx -y

# Instalar Git
sudo apt install git -y
```

---

### 2. Clonar o Projeto

```bash
# Criar diretório para aplicação
sudo mkdir -p /var/www/embuibe
sudo chown $USER:$USER /var/www/embuibe

# Clonar repositório (ou fazer upload via FTP/SCP)
cd /var/www/embuibe
git clone <URL-DO-REPOSITORIO> .

# OU fazer upload manual dos arquivos
# scp -r APP\ EMBUIBE/* usuario@servidor:/var/www/embuibe/
```

---

### 3. Configurar Backend

```bash
# Navegar para pasta do backend
cd /var/www/embuibe/backend

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux
# venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

#### Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
nano .env
```

Conteúdo do `.env`:

```env
# Banco de Dados
DATABASE_URL=sqlite:///./expresso_embuibe.db

# Segurança - IMPORTANTE: Gerar nova chave para produção!
SECRET_KEY=sua-chave-secreta-super-segura-aqui-min-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# CORS - Ajustar para domínio em produção
ALLOWED_ORIGINS=https://seudominio.com.br,https://www.seudominio.com.br

# Ambiente
ENVIRONMENT=production
```

**⚠️ IMPORTANTE**: Gere uma SECRET_KEY segura:

```bash
# Gerar SECRET_KEY aleatória
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

#### Inicializar Banco de Dados

```bash
# Criar tabelas
python create_tables.py

# Popular dados iniciais (cidades, motoristas, usuários)
python seed_data.py
```

**Usuários Padrão Criados:**
- **Admin**: login=`admin`, senha=`embuibe@2025`
- **Atendente Mariana**: login=`mariana`, senha=`2107`
- **Atendente Daniela**: login=`daniela`, senha=`2106`

🔒 **Alterar senhas após primeiro acesso!**

---

### 4. Configurar Serviço Systemd (Backend)

Criar arquivo de serviço:

```bash
sudo nano /etc/systemd/system/embuibe-backend.service
```

Conteúdo:

```ini
[Unit]
Description=Expresso Embuibe Backend API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/embuibe/backend
Environment="PATH=/var/www/embuibe/backend/venv/bin"
ExecStart=/var/www/embuibe/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ativar e iniciar serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable embuibe-backend
sudo systemctl start embuibe-backend
sudo systemctl status embuibe-backend
```

---

### 5. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/embuibe
```

Conteúdo:

```nginx
server {
    listen 80;
    server_name seudominio.com.br www.seudominio.com.br;

    # Frontend - Arquivos estáticos
    root /var/www/embuibe/frontend;
    index index.html;

    # Logs
    access_log /var/log/nginx/embuibe-access.log;
    error_log /var/log/nginx/embuibe-error.log;

    # Servir frontend
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy para Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Documentação da API (opcional)
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }

    location /redoc {
        proxy_pass http://127.0.0.1:8000/redoc;
        proxy_set_header Host $host;
    }
}
```

Ativar site:

```bash
sudo ln -s /etc/nginx/sites-available/embuibe /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### 6. Configurar SSL (HTTPS) com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado SSL
sudo certbot --nginx -d seudominio.com.br -d www.seudominio.com.br

# Renovação automática já está configurada!
```

---

## 🔧 Manutenção

### Ver Logs do Backend

```bash
sudo journalctl -u embuibe-backend -f
```

### Reiniciar Serviços

```bash
# Backend
sudo systemctl restart embuibe-backend

# Nginx
sudo systemctl reload nginx
```

### Atualizar Código

```bash
cd /var/www/embuibe
git pull origin main  # ou scp arquivos atualizados

# Reiniciar backend
sudo systemctl restart embuibe-backend
```

### Backup do Banco de Dados

```bash
# Criar backup
cp /var/www/embuibe/backend/expresso_embuibe.db \
   /var/backups/embuibe-$(date +%Y%m%d).db

# Automatizar backup diário (adicionar ao crontab)
sudo crontab -e

# Adicionar linha:
# 0 2 * * * cp /var/www/embuibe/backend/expresso_embuibe.db /var/backups/embuibe-$(date +\%Y\%m\%d).db
```

---

## 🧪 Teste em Produção

Após deploy, testar:

1. ✅ Acessar `https://seudominio.com.br`
2. ✅ Fazer login com usuário admin
3. ✅ Testar emissão de passagem
4. ✅ Testar cadastro de clientes
5. ✅ Testar relatórios
6. ✅ Verificar geração de PDF
7. ✅ Testar registro de saída
8. ✅ Verificar dashboards (atendente e admin)

---

## 🛡️ Segurança Pós-Deploy

### Checklist de Segurança:

- [ ] Alterar todas as senhas padrão
- [ ] Gerar nova SECRET_KEY (diferente de desenvolvimento)
- [ ] Configurar firewall (UFW):
  ```bash
  sudo ufw allow 22/tcp   # SSH
  sudo ufw allow 80/tcp   # HTTP
  sudo ufw allow 443/tcp  # HTTPS
  sudo ufw enable
  ```
- [ ] Configurar backups automáticos do banco
- [ ] Monitorar logs regularmente
- [ ] Manter sistema atualizado

---

## 📊 Monitoramento

### Verificar Status dos Serviços

```bash
# Backend API
sudo systemctl status embuibe-backend

# Nginx
sudo systemctl status nginx

# Ver processos Python
ps aux | grep uvicorn
```

### Análise de Performance

```bash
# Uso de CPU/Memória
htop

# Espaço em disco
df -h

# Logs de acesso do Nginx
tail -f /var/log/nginx/embuibe-access.log
```

---

## 🐛 Troubleshooting

### Problema: Backend não inicia

```bash
# Ver logs detalhados
sudo journalctl -u embuibe-backend -n 50

# Verificar se porta 8000 está ocupada
sudo lsof -i :8000

# Testar manualmente
cd /var/www/embuibe/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Problema: Frontend não carrega

```bash
# Verificar permissões
sudo chown -R www-data:www-data /var/www/embuibe/frontend

# Verificar config Nginx
sudo nginx -t

# Ver logs Nginx
tail -f /var/log/nginx/error.log
```

### Problema: Erro 502 Bad Gateway

```bash
# Verificar se backend está rodando
sudo systemctl status embuibe-backend

# Reiniciar backend
sudo systemctl restart embuibe-backend

# Verificar firewall
sudo ufw status
```

---

## 📱 Deploy Alternativo (Servidor Windows)

### Backend no Windows Server

```powershell
# Instalar Python 3.10+

# Criar ambiente virtual
cd C:\inetpub\wwwroot\embuibe\backend
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar como serviço com NSSM (Non-Sucking Service Manager)
nssm install EmbuibeBackend "C:\inetpub\wwwroot\embuibe\backend\venv\Scripts\uvicorn.exe" "app.main:app --host 0.0.0.0 --port 8000"
nssm start EmbuibeBackend
```

### Frontend no IIS

1. Copiar pasta `frontend` para `C:\inetpub\wwwroot\embuibe\`
2. Criar novo site no IIS apontando para essa pasta
3. Configurar proxy reverso para `/api/` → `http://localhost:8000/api/`

---

## 📞 Suporte

Para problemas ou dúvidas sobre o deploy:

1. Verificar logs: `sudo journalctl -u embuibe-backend -f`
2. Conferir configurações do `.env`
3. Validar status dos serviços com `systemctl`

---

**Sistema Pronto para Produção! ✅**

Última atualização: Dezembro 2025
