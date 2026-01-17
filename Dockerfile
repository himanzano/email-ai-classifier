FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instala uv
RUN pip install --no-cache-dir uv

# Copia arquivos de dependência
COPY pyproject.toml README.md ./

# Instala dependências (sem dev)
RUN uv sync --no-dev

# Copia o código
COPY app ./app
COPY static ./static

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
