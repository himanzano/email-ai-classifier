import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# --- Configuração do Python Path ---
# Adiciona a raiz do projeto ao sys.path para garantir que as importações
# absolutas (ex: `from app.services...`) funcionem, mesmo quando o script
# é executado de dentro de um subdiretório (como `app/main.py`).
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


# Importa o router do módulo da API (agora funciona, pois 'app' está no path)
from app.api import classify as classify_api

# --- Configuração Inicial ---

# Carrega variáveis de ambiente de um arquivo .env na raiz do projeto.
# Essencial para configurar chaves de API e outras configurações sem hardcoding.
BASE_DIR = project_root
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
    """
    return FileResponse(static_dir / "index.html")