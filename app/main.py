import sys
from pathlib import Path

# --- Configuração do Python Path ---
# O comando `fastapi run app/main.py` não adiciona a raiz do projeto ao
# PYTHONPATH, causando um ModuleNotFoundError. Este bloco corrige isso.
# Se você usar `uvicorn app.main:app`, este bloco não é necessário.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# --- Importações de Módulos ---
from app.api import classify as classify_api
from app.api import partials as partials_api # Rota para parciais de UI
from app.config import templates  # Importa da configuração central

# --- Configuração Inicial ---
BASE_DIR = project_root
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# --- Instância da Aplicação ---
app = FastAPI(
    title="Email AI Classifier",
    description="Uma aplicação completa para classificar e-mails e gerar respostas usando IA.",
    version="1.0.0"
)

# --- Montar Rotas e Arquivos Estáticos ---
app.include_router(classify_api.router)
app.include_router(partials_api.router) # Inclui o novo router
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# --- Rota Principal ---
@app.get("/", include_in_schema=False)
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "active_method": "text"}
    )