FROM python:3.12-slim

# Instalando dependencias do sistema, incluindo as do python3-saml
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    libxml2-dev libxmlsec1-dev libxmlsec1-openssl pkg-config && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala o Poetry globalmente
RUN pip install poetry==2.0.0

WORKDIR /app

# Desativa o .venv (instala pacotes diretamente no container)
RUN poetry config virtualenvs.create false

# Copia e instala dependências
COPY pyproject.toml poetry.lock* README.md ./
RUN poetry install --no-interaction --no-ansi --no-root

# Copia o código
COPY app/ ./app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]