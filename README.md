# Parcerias UFPA - API Backend

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

## Descrição
A API do **Parcerias UFPA** é o motor de backend responsável pelo gerenciamento de parcerias, dados institucionais e suporte aos usuários. 

O grande diferencial deste projeto é o seu **Módulo Assíncrono de Helpdesk via E-mail**. A API possui um robô nativo que monitora caixas de e-mail via IMAP e envia notificações via SMTP em background, sincronizando conversas externas diretamente no banco de dados através de tags de rastreamento (`[TICKET: UUID]`), garantindo que nenhuma demanda de suporte seja perdida.

## Tecnologias Principais
* **Framework Web:** FastAPI
* **ORM & Banco de Dados:** SQLModel / SQLAlchemy (Async) + PostgreSQL
* **Autenticação:** JWT (JSON Web Tokens)
* **Tarefas em Background:** Asyncio / Threads
* **Mensageria:** Protocolos IMAP (Leitura) e SMTP (Envio) nativos

## Requisitos (Requirements)
Antes de iniciar, certifique-se de ter instalado em sua máquina:
* Python 3.10+
* PostgreSQL (Local ou via Docker)
* Git

## Instalação e Configuração

1. **Clone o repositório:**
```bash
git clone https://gitlab.com/ccsl-ufpa/parcerias-ufpa.git
cd parcerias-ufpa

