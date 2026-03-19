import imaplib
import email
import re
import asyncio
import logging
import smtplib
from email.header import decode_header
from email.message import EmailMessage
from email.utils import parseaddr
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.db.db import async_engine 
from app.models.email_log import EmailLog
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Configurações do Gmail
SMTP_SERVER, SMTP_PORT = "smtp.gmail.com", 587
SMTP_USER = os.getenv("EMAIL_CONTA")
SMTP_PASSWORD = os.getenv("EMAIL_SENHA")

IMAP_SERVER = "imap.gmail.com"
EMAIL_CONTA, EMAIL_SENHA = SMTP_USER, SMTP_PASSWORD

# --- FUNÇÕES AJUDANTES (Deixam o código principal limpo) ---

def extrair_corpo_limpo(msg) -> str:
    """Extrai e limpa o texto do e-mail numa tacada só."""
    corpo = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                corpo = part.get_payload(decode=True).decode(errors="ignore")
                break
    else:
        corpo = msg.get_payload(decode=True).decode(errors="ignore")

    padroes_corte = [r"Em\s+.*?escreveu:", r"On\s+.*?wrote:", r"_{10,}", r"De:\s+.*?Enviado em:", r"From:\s+.*?Sent:", r"-{3,}\s*Mensagem original\s*-{3,}"]
    for p in padroes_corte:
        match = re.search(p, corpo, flags=re.IGNORECASE | re.DOTALL)
        if match: corpo = corpo[:match.start()]
        
    return corpo.strip()

def decodificar_assunto(msg) -> str:
    assunto_raw, encoding = decode_header(msg["Subject"])[0]
    if isinstance(assunto_raw, bytes):
        enc = "utf-8" if encoding in (None, "unknown-8bit") else encoding
        try: return assunto_raw.decode(enc, errors="ignore")
        except LookupError: return assunto_raw.decode("utf-8", errors="ignore")
    return assunto_raw

def processar_mensagem_bruta(raw_bytes) -> dict | None:
    """Transforma os bytes do IMAP num dicionário organizado."""
    msg = email.message_from_bytes(raw_bytes)
    
    # Ignora e-mails enviados pela própria API
    if msg.get("CHAVE") == "API_SISTEMA": return None

    assunto = decodificar_assunto(msg)
    match = re.search(r"\[TICKET:(.*?)\]", assunto)
    if not match: return None

    try:
        return {
            "email_resposta_de": UUID(match.group(1).strip()),
            "remetente": parseaddr(str(msg.get("From") or ""))[1],
            "destinatario": parseaddr(str(msg.get("To") or ""))[1],
            "assunto": assunto,
            "corpo": extrair_corpo_limpo(msg)
        }
    except ValueError:
        return None

# --- PROCESSOS PRINCIPAIS ---

def ler_emails_imap() -> list[dict]:
    respostas = []
    assinaturas_vistas = set() # Impede de adicionar o mesmo e-mail lido de pastas diferentes
    pastas = ["inbox", '"[Gmail]/E-mails enviados"', '"[Gmail]/Enviados"', '"[Gmail]/Sent Mail"', '"[Gmail]/Todos os e-mails"']

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_CONTA, EMAIL_SENHA)

        for pasta in pastas:
            if mail.select(pasta)[0] != 'OK': continue
            
            _, msgs = mail.search(None, 'ALL', 'SUBJECT', '"[TICKET:"')
            if not msgs[0]: continue

            for e_id in msgs[0].split():
                _, dados = mail.fetch(e_id, "(RFC822)")
                for resp_part in dados:
                    if isinstance(resp_part, tuple):
                        dados_msg = processar_mensagem_bruta(resp_part[1])
                        
                        if dados_msg:
                            assinatura = f"{dados_msg['email_resposta_de']}-{dados_msg['remetente']}-{dados_msg['corpo']}"
                            if assinatura not in assinaturas_vistas:
                                assinaturas_vistas.add(assinatura)
                                respostas.append(dados_msg)
        mail.logout()
    except Exception as e:
        logger.error(f"Erro IMAP: {e}")
    
    return respostas

async def loop_leitura_emails():
    AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    logger.info("Robô de leitura de e-mails iniciado em background.")
    
    while True:
        try:
            novos_emails = await asyncio.to_thread(ler_emails_imap)
            
            if novos_emails:
                async with AsyncSessionLocal() as session:
                    for d in novos_emails:
                        # Ignora se o e-mail pai já não existir no banco
                        if d["email_resposta_de"] and not (await session.execute(select(EmailLog).where(EmailLog.id == d["email_resposta_de"]))).scalars().first():
                            continue 
                        
                        # Anti-duplicidade no banco de dados
                        query_existe = select(EmailLog).where(EmailLog.remetente == d["remetente"], EmailLog.corpo == d["corpo"])
                        if not (await session.execute(query_existe)).scalars().first():
                            session.add(EmailLog(**d))
                            await session.flush() 
                            logger.info(f"✅ Nova resposta de {d['remetente']} salva!")
                    
                    await session.commit()
        except Exception as e:
            logger.error(f"Erro no ciclo do robô: {e}")
            
        await asyncio.sleep(300)

def disparar_email_gmail_sync(msg: EmailMessage):
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()

async def enviar_email_interesse_background(
    session: AsyncSession, remetente: str, nome_remetente: str ,assunto: str, corpo: str, interesse_id: UUID | None = None,
):
    id_deste_email = uuid4()
    assunto_final = assunto if "[TICKET:" in assunto else f"{assunto} [TICKET:{id_deste_email}]"

    corpo_formatado = (
        f"🚨 NOVA DEMANDA 🚨\n nome do usuário: {nome_remetente}\n \n Email do usuário: {remetente}\n"
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
        
        session.add(EmailLog(
            id=id_deste_email, interesse_id=interesse_id, email_resposta_de=None, 
            remetente=remetente, destinatario=SMTP_USER, assunto=assunto_final, corpo=corpo
        ))
        await session.commit()
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail: {e}")