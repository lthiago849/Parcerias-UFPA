import imaplib
import email
import re
import asyncio
import logging
import smtplib
from email.header import decode_header
from email.message import EmailMessage
from uuid import UUID, uuid4

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.db.db import async_engine 
from app.models.email_log import EmailLog

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "lthiago849@gmail.com" 
SMTP_PASSWORD = "rlqw ryqy dphi pzct" 

IMAP_SERVER = "imap.gmail.com"
EMAIL_CONTA = "lthiago849@gmail.com" 
EMAIL_SENHA = "rlqw ryqy dphi pzct" 

def extrair_corpo_email(msg):
    if msg.is_multipart():
        for part in msg.walk():
            conteudo_tipo = part.get_content_type()
            disposicao = str(part.get("Content-Disposition"))
            if "attachment" not in disposicao and conteudo_tipo == "text/plain":
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()
    return ""

def ler_emails_imap():
    respostas_encontradas = []
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_CONTA, EMAIL_SENHA)
        mail.select("inbox")

        status, mensagens = mail.search(None, "UNSEEN")
        if not mensagens[0]:
            mail.logout()
            return respostas_encontradas

        ids_emails = mensagens[0].split()

        for e_id in ids_emails:
            status, dados = mail.fetch(e_id, "(RFC822)")
            for resposta_part in dados:
                if isinstance(resposta_part, tuple):
                    msg = email.message_from_bytes(resposta_part[1])
                    
                    assunto_raw, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(assunto_raw, bytes):
                        assunto = assunto_raw.decode(encoding or "utf-8")
                    else:
                        assunto = assunto_raw

                    remetente = msg.get("From")
                    corpo = extrair_corpo_email(msg)

                    match = re.search(r"\[TICKET:(.*?)\]", assunto)
                    if match:
                        ticket_str = match.group(1).strip()
                        id_original = None
                        try:
                            id_original = UUID(ticket_str)
                        except ValueError:
                            logger.warning(f"O TICKET '{ticket_str}' não é um UUID válido.")
                            
                        respostas_encontradas.append({
                            "email_resposta_de": id_original, # Usa a sua nova coluna
                            "remetente": remetente,
                            "assunto": assunto,
                            "corpo": corpo
                        })
        mail.logout()
    except Exception as e:
        logger.error(f"Erro ao ler e-mails (IMAP): {e}")
    
    return respostas_encontradas

async def loop_leitura_emails():
    AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    logger.info("Robô de leitura de e-mails iniciado em background.")
    
    while True:
        try:
            novos_emails = await asyncio.to_thread(ler_emails_imap)
            
            if novos_emails:
                async with AsyncSessionLocal() as session:
                    for dados in novos_emails:
                        novo_log = EmailLog(
                            email_resposta_de=dados["email_resposta_de"], # Salva na sua coluna
                            remetente=dados["remetente"],
                            destinatario=EMAIL_CONTA,
                            assunto=dados["assunto"],
                            corpo=dados["corpo"]
                        )
                        session.add(novo_log)
                        logger.info("Preparando para salvar uma resposta atrelada ao e-mail original...")
                    
                    await session.commit()
                    logger.info("✅ Resposta(s) salva(s) com sucesso no banco de dados!")
        except Exception as e:
            logger.error(f"Erro fatal no ciclo do robô: {e}")
            
        await asyncio.sleep(1200)

async def enviar_email_interesse_background(
    session: AsyncSession, remetente: str, destinatario: str, assunto: str, corpo: str, interesse_id: UUID | None = None,
):
    # Gera o ID deste e-mail para mandar no TICKET
    id_deste_email = uuid4()

    if "[TICKET:" not in assunto:
        assunto_final = f"{assunto} [TICKET: {id_deste_email}]"
    else:
        assunto_final = assunto

    msg = EmailMessage()
    msg.set_content(corpo)
    msg["Subject"] = assunto_final
    msg["From"] = remetente
    msg["To"] = destinatario

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"📧 E-mail disparado para {destinatario} com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail pelo Gmail: {e}")

    novo_log = EmailLog(
        id=id_deste_email, 
        interesse_id=interesse_id,
        email_resposta_de=None, # Como é o primeiro envio, não é resposta de ninguém
        remetente=remetente, 
        destinatario=destinatario, 
        assunto=assunto_final, 
        corpo=corpo
    )
    session.add(novo_log)
    await session.commit()