from fastapi.templating import Jinja2Templates
from pathlib import Path

# Obtém o diretório base do projeto de forma robusta
BASE_DIR = Path(__file__).resolve().parent.parent

# Instância única e centralizada do Jinja2Templates
# Usar um caminho absoluto (resolvido) torna a localização dos templates mais confiável
templates = Jinja2Templates(directory=str(BASE_DIR / "app/templates"))
