import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    "Classe de configuração globais da biblioteca e do pipeline usando variáveis de ambiente."

    # Pastas com os caminhos necessários para salvar os arquivos logs etc.
    DIR_RAW_EMAIL: str = os.getenv("DIR_RAW_EMAIL", "./data/emails")
    DIR_INCOMING: str = os.getenv("DIR_INCOMING", "./data/incoming")
    DIR_PROCESSED: str = os.getenv("DIR_PROCESSED", "./data/processed")
    DIR_TRANSFORMED: str = os.getenv("DIR_TRANSFORMED", "./data/transformed")
    DIR_LOGS: str = os.getenv("DIR_LOGS", "./logs")

    # Nota: Usamos Optional[str] para indicar que a variável pode ser None se não for definida.
    
    EMAIL_IN: Optional[str] = os.getenv("EMAIL_IN")
    EMAIL_PORT: Optional[int] = os.getenv("EMAIL_PORT", 993)
    EMAIL_IN: Optional[str] = os.getenv("EMAIL_IN")
    EMAIL_PWD: Optional[str] = os.getenv("EMAIL_PWD")
    
    # --- Configurações Gerais ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def validate_email_settings(self):
        """Verifica se as credenciais de e-mail estão definidas."""
        if not all([self.EMAIL_IN, self.EMAIL_IN, self.EMAIL_PWD]):
            print("[AVISO CRÍTICO] As variáveis de ambiente EMAIL_HOST, EMAIL_USER e EMAIL_PASSWORD não estão totalmente definidas. O EmailExtractor pode falhar.")

    MYSQL_CONN = os.getenv("MYSQL_CONN")
    POSTGRES_CONN = os.getenv("POSTGRES_CONN")
    MONGO_CONN = os.getenv("MONGO_CONN")

settings = Settings()
settings.validate_email_settings()