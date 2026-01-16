from typing import Union

from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path

# Resolver o path garante previsibilidade independente do local de execução.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)  # Carrega variáveis de ambiente do arquivo .env

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}