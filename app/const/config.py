import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN_EXPIRES_MINUTES = int(100000)
CHANGE_PASSWORD_TOKEN_EXPIRE_MINUTES = os.getenv("CHANGE_PASSWORD_TOKEN", 15)
SECRET_KEY = os.getenv("SECRET_KEY", "developer_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
