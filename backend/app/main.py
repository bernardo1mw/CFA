"""
Aplicação principal FastAPI para o sistema de reconhecimento de placas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from .routers import placas

# Carrega variáveis de ambiente
load_dotenv()

# Cria pasta de upload se não existir
upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
os.makedirs(upload_folder, exist_ok=True)

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="PlacaView API",
    description="API para reconhecimento automático de placas de veículos",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configura CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os routers
app.include_router(placas.router, prefix="/api/v1")

# Serve arquivos estáticos (se necessário)
if os.path.exists(upload_folder):
    app.mount("/uploads", StaticFiles(directory=upload_folder), name="uploads")


@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "PlacaView API - Sistema de Reconhecimento de Placas",
        "version": "2.0.0",
        "docs": "/docs",
        "api_version": "v1",
        "endpoints": {
            "placas": "/api/v1/placas",
            "health": "/api/v1/health",
            "clean": "/api/v1/placas/admin/clean"
        }
    }


@app.get("/api/v1/health")
async def health_check():
    """Endpoint para verificação de saúde da API."""
    return {"status": "healthy", "message": "API funcionando corretamente"}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
