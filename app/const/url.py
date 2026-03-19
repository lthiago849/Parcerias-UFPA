import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# --- SISTEMA DE RAIO-X PARA OS LOGS DO KOYEB ---
print("\n" + "="*40)
print("🔍 DEBUG DE CONEXÃO DO BANCO DE DADOS")
if DATABASE_URL:
    # Mostra apenas o início da URL para não vazar a sua senha nos logs
    print(f"✅ Variavel encontrada no Koyeb: {DATABASE_URL[:30]}...")
else:
    print("❌ ALERTA: A variavel DATABASE_URL esta VAZIA ou nao foi encontrada!")
print("="*40 + "\n")
# -----------------------------------------------

# Se a DATABASE_URL não estiver definida no Koyeb, monta a URL para o localhost/Docker
if not DATABASE_URL:
    DOCKER_COMPOSE = os.getenv("DOCKER_COMPOSE")
    ENV_DATABASE_URL = os.getenv("ENV_DATABASE_URL")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "parcerias_ufpa-v1")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "PARCERIAS_UFPA_DB")

    if ENV_DATABASE_URL:
        DATABASE_URL = f"postgresql+asyncpg://postgres:{ENV_DATABASE_URL}"
    elif DOCKER_COMPOSE == "true":
        DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"
    else:
        DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"