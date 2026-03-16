import imaplib
import email
import re
import asyncio
from email.header import decode_header
from sqlmodel import Session
from app.db.db import get_session 
from app.models.email_log import EmailLog
import smtplib
from email.message import EmailMessage
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

# Configurações do seu servidor de E-mail (idealmente colocar no .env)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "seu_email_sistema@gmail.com"
SMTP_PASSWORD = "sua_senha_de_app"
# Configurações do seu e-mail (O mesmo usado para enviar)
IMAP_SERVER = "imap.gmail.com"
EMAIL_CONTA = "seu_email_sistema@gmail.com"
EMAIL_SENHA = "sua_senha_de_app_do_google" # Tem de ser a senha de app!

def extrair_corpo_email(msg):
    """Função auxiliar para pegar apenas o texto do e-mail (ignora anexos)"""
    if msg.is_multipart():
        for part in msg.walk():
            conteudo_tipo = part.get_content_type()
            disposicao = str(part.get("Content-Disposition"))
            if "attachment" not in disposicao and conteudo_tipo == "text/plain":
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()
    return ""

def verificar_caixa_entrada():
    """Conecta ao Gmail, lê os Não Lidos e salva no banco"""
    try:
        # 1. Conecta ao Gmail
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_CONTA, EMAIL_SENHA)
        mail.select("inbox")

        # 2. Procura apenas e-mails NÃO LIDOS (UNSEEN)
        status, mensagens = mail.search(None, "UNSEEN")
        ids_emails = mensagens[0].split()

        if not ids_emails:
            return # Não há mensagens novas

        # 3. Abre uma sessão com o banco de dados
        with Session(get_session) as session:
            for e_id in ids_emails:
                status, dados = mail.fetch(e_id, "(RFC822)")
                for resposta_part in dados:
                    if isinstance(resposta_part, tuple):
                        msg = email.message_from_bytes(resposta_part[1])
                        
                        # Extrai o Assunto e decodifica
                        assunto_raw, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(assunto_raw, bytes):
                            assunto = assunto_raw.decode(encoding or "utf-8")
                        else:
                            assunto = assunto_raw

                        # Extrai o Remetente
                        remetente = msg.get("From")
                        
                        # Extrai o Corpo do E-mail
                        corpo = extrair_corpo_email(msg)

                        # 4. A MÁGICA: Procura o [TICKET: id-do-interesse] no assunto usando Regex
                        match = re.search(r"\[TICKET:(.*?)\]", assunto)
                        
                        if match:
                            interesse_id_str = match.group(1).strip()
                            
                            # Salva a resposta do utilizador no Banco de Dados!
                            novo_log = EmailLog(
                                interesse_id=interesse_id_str, # Liga ao interesse correto
                                remetente=remetente,
                                destinatario=EMAIL_CONTA,
                                assunto=assunto,
                                corpo=corpo
                            )
                            session.add(novo_log)
                            session.commit()
                            print(f"✅ Resposta salva para o Ticket {interesse_id_str}")

        mail.logout()
    except Exception as e:
        print(f"Erro ao ler e-mails: {e}")

async def loop_leitura_emails():
    """Roda a verificação de e-mails num loop infinito a cada 2 minutos"""
    while True:
        # Usamos asyncio.to_thread para não congelar a sua API enquanto lê os e-mails
        await asyncio.to_thread(verificar_caixa_entrada)
        # Espera 120 segundos (2 minutos) antes de verificar a caixa de entrada de novo
        await asyncio.sleep(120)


async def enviar_email_interesse_background(
    session: AsyncSession, 
    interesse_id: UUID,
    remetente: str, 
    destinatario: str, 
    assunto: str, 
    corpo: str
):
    """
    1. Envia o e-mail de verdade (SMTP).
    2. Guarda o histórico na tabela email_log.
    """
    # ==========================================
    # 1. TENTA ENVIAR O E-MAIL
    # ==========================================
    msg = EmailMessage()
    msg.set_content(corpo)
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    try:
        # ATENÇÃO: Se não quiser enviar e-mails de verdade agora nos testes, 
        # pode comentar estas 4 linhas abaixo e ele apenas guardará no banco!
        # server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        # server.starttls()
        # server.login(SMTP_USER, SMTP_PASSWORD)
        # server.send_message(msg)
        # server.quit()
        pass
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        # Mesmo dando erro no envio, queremos guardar no banco para auditar!

    # ==========================================
    # 2. GUARDA O REGISTO NO BANCO DE DADOS
    # ==========================================
    novo_log = EmailLog(
        interesse_id=interesse_id,
        remetente=remetente,
        destinatario=destinatario,
        assunto=assunto,
        corpo=corpo
    )
    
    session.add(novo_log)
    await session.commit()