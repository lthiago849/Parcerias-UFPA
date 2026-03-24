from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager

from app.views import router
from app.controllers.email import loop_leitura_emails

@asynccontextmanager
async def lifespan(app: FastAPI):
    tarefa_emails = asyncio.create_task(loop_leitura_emails())
    print("🤖 Robô de leitura de e-mails iniciado!")
    
    yield 
    
    tarefa_emails.cancel()
    print("🛑 Robô de leitura de e-mails desligado!")

app = FastAPI(
    title="Parcerias UFPA API",
    version="1.0.0",
    lifespan=lifespan  
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)