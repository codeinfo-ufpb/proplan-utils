import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    "Classe de configuração globais da biblioteca."
    MYSQL_CONN = os.getenv("MYSQL_CONN")
    POSTGRES_CONN = os.getenv("POSTGRES_CONN")
    MONGO_CONN = os.getenv("MONGO_CONN")

settings = Settings()