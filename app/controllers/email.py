import imaplib
import email
import re
import asyncio
import logging
import smtplib
import os
from dotenv import load_dotenv
from pathlib import Path
from email.header import decode_header
from email.message import EmailMessage
from email.utils import parseaddr
from uuid import UUID, uuid4
from fastapi import HTTPException

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.db.db import async_engine 
from app.models.email import Email
from app.models.mensagem import Mensagem 
from app.const.enums import tipo_status
from app.utils.email import (
    ler_emails_imap,
    disparar_email_gmail_sync
    )

CAMINHO_ENV = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=CAMINHO_ENV, override=True)

# Configurações do Gmail
SMTP_SERVER, SMTP_PORT = "smtp.gmail.com", 587
SMTP_USER = os.getenv("EMAIL_CONTA")
SMTP_PASSWORD = os.getenv("EMAIL_SENHA")

IMAP_SERVER = "imap.gmail.com"
EMAIL_CONTA, EMAIL_SENHA = SMTP_USER, SMTP_PASSWORD

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

async def loop_leitura_emails():
    AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    logger.info("Robô de leitura de e-mails iniciado em background.")
    
    while True:
        try:
            novos_emails = await asyncio.to_thread(ler_emails_imap)
            
            if novos_emails:
                async with AsyncSessionLocal() as session:
                    for d in novos_emails:
                        
                        # 1. Verifica se a Conversa (Ticket) realmente existe
                        if d["email_id"]:
                            query_conversa = select(Email).where(Email.id == d["email_id"])
                            conversa_existe = (await session.execute(query_conversa)).scalars().first()
                            if not conversa_existe:
                                # O ALARME AQUI: Avisa que o Ticket não existe no banco!
                                logger.warning(f"⚠️ Ignorado: O Ticket {d['email_id']} não existe no banco de dados. (E-mail de teste antigo?)")
                                continue 
                        
                        # 2. Anti-duplicidade
                        query_existe = select(Mensagem).where(
                            Mensagem.email_id == d["email_id"],
                            Mensagem.remetente == d["remetente"], 
                            Mensagem.corpo == d["corpo"]
                        )
                        if (await session.execute(query_existe)).scalars().first():
                            # O ALARME AQUI: Avisa que já leu esta mensagem antes!
                            logger.info(f"🔄 Ignorado: A resposta de {d['remetente']} já foi salva anteriormente.")
                        else:
                            # Salva a nova mensagem
                            session.add(Mensagem(**d))
                            await session.flush() 
                            logger.info(f"✅ Nova resposta de {d['remetente']} anexada ao Ticket {d['email_id']}!")
                    
                    await session.commit()
        except Exception as e:
            logger.error(f"Erro no ciclo do robô: {e}")
            
        await asyncio.sleep(300)



async def enviar_email_interesse_background(
    session: AsyncSession, remetente: str, nome_remetente: str, assunto: str, corpo: str, interesse_id: UUID | None = None,
):
    id_deste_email = uuid4()
    assunto_final = assunto if "[TICKET:" in assunto else f"{assunto} [TICKET:{id_deste_email}]"

    corpo_formatado = (
        f"🚨 NOVA DEMANDA 🚨\nNome do usuário: {nome_remetente}\nEmail do usuário: {remetente}\n"
        f"----------------------------------------\n\n{corpo}\n\n----------------------------------------\n"
        f"⚠️ ATENÇÃO: Para responder a este usuário e registrar no sistema, APENAS CLIQUE EM 'RESPONDER' neste e-mail."
    )

    msg = EmailMessage()
    msg.set_content(corpo_formatado)
    msg["Subject"] = assunto_final
    msg["From"] = f"Sistema <{SMTP_USER}>" 
    msg["To"] = SMTP_USER
    msg["Reply-To"] = remetente
    msg["CHAVE"] = "API_SISTEMA"

    try:
        await asyncio.to_thread(disparar_email_gmail_sync, msg)
        logger.info(f"📧 E-mail disparado para {SMTP_USER} com sucesso!")
    except Exception as e:
        logger.error(f"🚨 Erro ao enviar o e-mail físico (SMTP): {e}")
        return # Se o e-mail falhar, interrompe tudo e nem tenta salvar no banco
        
    # 2. SE O E-MAIL FOI, TENTA SALVAR NO BANCO DE DADOS
    try:
        nova_conversa = Email(
            id=id_deste_email,
            interesse_id=interesse_id,
            assunto_principal=assunto_final,
            status=tipo_status.ATIVO
        )
        session.add(nova_conversa)
        
        primeira_mensagem = Mensagem(
            email_id=id_deste_email,
            remetente=remetente,
            destinatario=SMTP_USER,
            corpo=corpo
        )
        session.add(primeira_mensagem)
        
        await session.commit()
        logger.info(f"✅ Ticket {id_deste_email} salvo no banco com sucesso!")
    except Exception as e:
        await session.rollback() 
        logger.error(f"🚨 ERRO CRÍTICO AO SALVAR NO BANCO DE DADOS: {e}")


async def trocar_status_email(
    email_id : UUID,
    db: AsyncSession
):
    
    query = select(Email
        ).where(Email.id == email_id)
    result = await db.execute(query)
    email = result.scalars().first() 

    if not email:
        raise HTTPException(status_code=404, detail="Ticket de e-mail não encontrado.")
    
    if email.status == tipo_status.ATIVO:
        email.status = tipo_status.ENCERRADO
    else:
        email.status = tipo_status.ATIVO

    db.add(email)
    await db.commit()
    await db.refresh(email)

    return {
        "mensagem": "Status alteado com sucesso.",
        "email_id": email.id,
        "novo_status": email.status.value
    }


async def enviar_mensagem(
    email_id: UUID,
    corpo: str,
    remetente: str,
    destinatario: str,
    db: AsyncSession
):
    
    query = select(email).where(email.id == email_id)
    result = await db.execute(query)
    email = result.scalars().first()

    if not email:
        raise HTTPException(status_code = 404, detail = "Email nao encontrado")
    
    nova_mensagem = Mensagem(
        email_id = email_id,
        remetente = remetente,
        destinatario = destinatario,
        corpo = corpo
    )

    db.add(nova_mensagem)
    await db.commit()
    await db.refresh(nova_mensagem)

    return nova_mensagem


async def disparar_resposta_ticket_background(
    session: AsyncSession,
    email_id: UUID,
    usuario_logado, # Recebemos os dados de quem está respondendo
    corpo: str
):
    # 1. Busca o Ticket para pegar o Assunto
    query_ticket = select(Email).where(Email.id == email_id)
    ticket = (await session.execute(query_ticket)).scalars().first()
    
    if not ticket:
        logger.error(f"Ticket {email_id} não encontrado para resposta.")
        return

    # MÁGICA 2: Busca a PRIMEIRA mensagem deste ticket para descobrir quem é o cliente original
    query_primeira_msg = select(Mensagem).where(Mensagem.email_id == email_id).order_by(Mensagem.enviado_em.asc())
    primeira_msg = (await session.execute(query_primeira_msg)).scalars().first()

    if not primeira_msg:
        logger.error("Nenhuma mensagem anterior encontrada para extrair o destinatário.")
        return

    # Define automaticamente os e-mails
    destinatario_cliente = primeira_msg.remetente # O cliente que abriu o chamado
    remetente_dev = usuario_logado.email # O e-mail do desenvolvedor logado no sistema

    # 2. Monta o E-mail físico
    msg = EmailMessage()
    msg.set_content(corpo)
    msg["Subject"] = ticket.assunto_principal
    
    # Deixa o e-mail bonitinho: "Nome do Dev (Via Sistema) <emaildosistema@gmail.com>"
    msg["From"] = f"{usuario_logado.nome} (Via Sistema) <{SMTP_USER}>" 
    
    msg["To"] = destinatario_cliente
    msg["Reply-To"] = f"{destinatario_cliente}, {SMTP_USER}"
    msg["CHAVE"] = "API_SISTEMA" 

    # 3. Tenta enviar o e-mail via Gmail primeiro
    try:
        await asyncio.to_thread(disparar_email_gmail_sync, msg)
        logger.info(f"📧 Resposta de {usuario_logado.nome} enviada para {destinatario_cliente} com sucesso!")
    except Exception as e:
        logger.error(f"🚨 Erro ao enviar resposta via SMTP: {e}")
        return 

    # 4. Se o e-mail foi, salva no banco de dados
    try:
        nova_mensagem = Mensagem(
            email_id=email_id,
            remetente=remetente_dev, # Fica registrado no banco EXATAMENTE qual dev respondeu
            destinatario=destinatario_cliente,
            corpo=corpo
        )
        session.add(nova_mensagem)
        await session.commit()
        logger.info(f"✅ Resposta anexada ao banco do ticket {email_id}!")
    except Exception as e:
        await session.rollback()
        logger.error(f"🚨 Erro ao salvar resposta no banco: {e}")