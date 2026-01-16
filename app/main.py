from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Importa o router do módulo da API
from app.api import classify as classify_api

# --- Configuração Inicial ---

# Carrega variáveis de ambiente de um arquivo .env na raiz do projeto.
# Essencial para configurar chaves de API e outras configurações sem hardcoding.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# --- Criação da Aplicação FastAPI ---

app = FastAPI(
    title="Email AI Classifier",
    description="Uma aplicação completa para classificar e-mails e gerar respostas usando IA.",
    version="1.0.0"
)

# --- Inclusão de Rotas (Routers) ---

# Inclui o router definido em `api/classify.py`.
# Todas as rotas definidas lá serão adicionadas à aplicação principal.
app.include_router(classify_api.router)


# --- Servir Arquivos Estáticos (Frontend) ---

# Monta o diretório 'static' para que o FastAPI possa servir os arquivos
# HTML, CSS e JS da interface web.
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
async def root():
    """
    Endpoint raiz que serve o arquivo `index.html` do frontend.
    `include_in_schema=False` evita que esta rota de UI apareça na documentação
    automática da API (ex: /docs).
    """
    return FileResponse(static_dir / "index.html")
