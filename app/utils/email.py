import imaplib
import email
import re
import logging
import smtplib
import os
from dotenv import load_dotenv
from pathlib import Path
from email.header import decode_header
from email.message import EmailMessage
from email.utils import parseaddr
from uuid import UUID



CAMINHO_ENV = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=CAMINHO_ENV, override=True)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Configurações do Gmail
SMTP_SERVER, SMTP_PORT = "smtp.gmail.com", 587
SMTP_USER = os.getenv("EMAIL_CONTA")
SMTP_PASSWORD = os.getenv("EMAIL_SENHA")

IMAP_SERVER = "imap.gmail.com"
EMAIL_CONTA, EMAIL_SENHA = SMTP_USER, SMTP_PASSWORD

# --- FUNÇÕES AJUDANTES ---

def extrair_corpo_limpo(msg) -> str:
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
    msg = email.message_from_bytes(raw_bytes)
    
    if msg.get("CHAVE") == "API_SISTEMA": return None

    assunto = decodificar_assunto(msg)
    match = re.search(r"\[TICKET:(.*?)\]", assunto)
    if not match: return None

    # ADICIONE ESTA LINHA AQUI PARA VER A MÁGICA NO TERMINAL:
    logger.info(f"🔍 O Robô encontrou uma resposta do Ticket: {match.group(1)}")

    try:
        return {
            "email_id": UUID(match.group(1).strip()),
            "remetente": parseaddr(str(msg.get("From") or ""))[1],
            "destinatario": parseaddr(str(msg.get("To") or ""))[1],
            "corpo": extrair_corpo_limpo(msg)
        }
    except ValueError:
        return None

# --- PROCESSOS PRINCIPAIS ---

def ler_emails_imap() -> list[dict]:
    respostas = []
    assinaturas_vistas = set()
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
                            assinatura = f"{dados_msg['email_id']}-{dados_msg['remetente']}-{dados_msg['corpo']}"
                            if assinatura not in assinaturas_vistas:
                                assinaturas_vistas.add(assinatura)
                                respostas.append(dados_msg)
        mail.logout()
    except Exception as e:
        logger.error(f"Erro IMAP: {e}")
    
    return respostas


def disparar_email_gmail_sync(msg: EmailMessage):
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()
