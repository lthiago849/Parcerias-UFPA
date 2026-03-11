# ==========================================
# ESTÁGIO 1: BUILD ENVIRONMENT
# ==========================================
FROM python:3.12-slim AS build-environment

# Instala ferramentas do sistema necessárias para compilar dependências
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VERSION=2.0.0

# Instala o Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION \
    && ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry

# Garante que o ambiente virtual seja criado na pasta /app/.venv
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app

# Copia os arquivos de dependência primeiro
COPY pyproject.toml poetry.lock* README.md ./

# Instala as dependências (sem tentar instalar o projeto em si)
RUN poetry install --no-interaction --no-ansi --no-root

# ==========================================
# ESTÁGIO 2: RUNTIME ENVIRONMENT
# ==========================================
FROM python:3.12-slim AS runtime-environment

# Instala apenas a biblioteca de execução do Postgres (mais leve que a de compilação)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia O ambiente virtual (.venv) e os arquivos de configuração do estágio de build
COPY --from=build-environment /app /app

# Copia o código real da aplicação
COPY app/ ./app/

# Variáveis do seu modelo SAIA
ARG basepath
ENV BASEPATH=$basepath

ARG senhaemail
ENV SENHA_DO_EMAIL=$senhaemail

# Coloca o ambiente virtual no PATH (assim o Python já roda direto do .venv)
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Comando para iniciar o servidor
CMD sh -c 'uvicorn app.main:app --host 0.0.0.0 --port 8000 --root-path "${BASEPATH:-/}"'