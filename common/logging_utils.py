from os import makedirs
import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

def get_logger(name: str = "etl", name_file: str = "pipeline", **kwargs) -> logging.Logger:
    """
    Cria e configura um logger robusto para uso corporativo.
    - Registra logs tanto no console quanto em arquivo (rotativo).
    - Garante que logs antigos não cresçam indefinidamente.
    - Formata mensagens com timestamp, nível e origem.
    """
    # Cria a pasta logs caso não exista.
    makedirs("logs", exist_ok=True)

    # Exemplo do nome do arquivo que será criado no arquivo de logs: logs/pipeline_2025-10-24.log
    date_suffix = datetime.now().strftime("%Y-%m-%d")
    log_file = f"logs/{name_file}_{date_suffix}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        fmt = logging.Formatter(
            "%(asctime)s [%(name)s:%(lineno)d] %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(fmt)
        logger.addHandler(stream_handler)

        # Arquivo rotativo — limite 1 MB, 5 backups
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=1 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    return logger
