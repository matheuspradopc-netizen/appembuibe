"""
Aplicação principal - Expresso Embuibe
Sistema de gestão de transporte de passageiros
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .config import settings
from .database import init_db

# Cria a aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema web para gestão de transporte de passageiros - emissão de passagens, relatórios e controle de viagens"
)

# Configuração do CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens em desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Evento executado ao iniciar a aplicação.
    Inicializa o banco de dados.
    """
    init_db()
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} iniciado!")


@app.get("/api/v1")
async def root():
    """
    Endpoint raiz da API - Health check
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online"
    }


@app.get("/api/v1/health")
async def health():
    """
    Endpoint de verificação de saúde da API
    """
    return {"status": "healthy"}


# Import e registro dos routers
from .routers import auth, clientes, passagens, relatorios, viagens, dashboard, auxiliares
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticação"])
app.include_router(clientes.router, prefix="/api/v1/clientes", tags=["Clientes"])
app.include_router(passagens.router, prefix="/api/v1/passagens", tags=["Passagens"])
app.include_router(relatorios.router, prefix="/api/v1/relatorios", tags=["Relatórios"])
app.include_router(viagens.router, prefix="/api/v1/viagens", tags=["Viagens"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(auxiliares.router, prefix="/api/v1", tags=["Auxiliares"])

# Servir arquivos estáticos do frontend em produção
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"

if FRONTEND_DIR.exists():
    # Serve arquivos estáticos (CSS, JS, páginas)
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
    app.mount("/pages", StaticFiles(directory=FRONTEND_DIR / "pages", html=True), name="pages")
    if (FRONTEND_DIR / "admin").exists():
        app.mount("/admin", StaticFiles(directory=FRONTEND_DIR / "admin", html=True), name="admin")
    if (FRONTEND_DIR / "atendente").exists():
        app.mount("/atendente", StaticFiles(directory=FRONTEND_DIR / "atendente", html=True), name="atendente")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        # Não intercepta rotas da API
        if full_path.startswith("api/"):
            return {"detail": "Not found"}

        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # Fallback para index.html (SPA)
        return FileResponse(FRONTEND_DIR / "index.html")
