
import os
import shutil
import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
import zipfile
from pathlib import Path
from common.logging_utils import get_logger

logger = get_logger("file-utils")

# Diretório para enviar os arquivos excluídos. Caso não exista será criado.
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
TRASH_DIR = ROOT_DIR / "data" / "trash"
TRASH_DIR.mkdir(parents=True, exist_ok=True)

def get_logger(name: str = "etl", name_file: str = "pipeline", **kwargs) -> logging.Logger:
    """
    Cria e configura um logger robusto para uso corporativo.
    - Registra logs tanto no console quanto em arquivo (rotativo).
    """
    LOG_DIR = Path("logs")
    LOG_DIR.mkdir(exist_ok=True)

    # Nome do arquivo de log: logs/pipeline_YYYY-MM-DD.log
    date_suffix = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"{name_file}_{date_suffix}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # CRÍTICO: Impede que as mensagens se propaguem para o logger raiz, 
    # garantindo que nossos handlers de arquivo personalizados sejam usados.
    logger.propagate = False 

    # Impede que o logger adicione handlers duplicados em re-execuções
    if not logger.handlers:
        fmt = logging.Formatter(
            "%(asctime)s [%(name)s:%(lineno)d] %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler (saída padrão)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(fmt)
        logger.addHandler(stream_handler)

        # Arquivo rotativo (File Handler)
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=1 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
        
    return logger


def move_to_trash(file_path: str):
    """
    Move um arquivo para a pasta .trash (Lixeira com os arquivos apagados).
    """
    try:
        src = Path(file_path)
        if not src.exists():
            logger.warning(f" [AVISO] A Pasta não possui arquivo para ser movido..: {file_path}")
            return False
        dst = TRASH_DIR / src.name
        shutil.move(str(src), str(dst))
        logger.info(f" [OK] O arquivo encontrado foi movido para a lixeira. Arquivo: {dst}")
        return True
    except Exception as e:
        logger.error(f"Ops! [ERRO] Não foi possível mover o arquivo para lixeira: {file_path}. Erro: {e}")
        return False

def extract_zip(zip_path: str, output_dir: str = None) -> list[str]:
    """
    Realiza a extração dos arquivos que estejam em um arquivo .zip para a pasta output_dir.
    - Retorna uma lista com os arquivos arquivos extraídos.
    """
    output_dir = Path(output_dir or Path(zip_path).parent)
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted_files = []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
            extracted_files = [str(Path(output_dir) / f) for f in zip_ref.namelist()]
        logger.info(f" [OK] Os arquivos foram extraídos! Lista dos arquivos com os nomes dos arquivos da pasta ZIP: {extracted_files}")
    except Exception as e:
        logger.error(f"Ops! [ERRO] Falha ao extrair arquivos da pasta ZIP {zip_path}: {e}")
    
    return extracted_files

def extract_and_trash_zip(zip_path: str, output_dir: str = None) -> list[str]:
    """
    Extrairá um arquivo do tipo ZIP e moverá o arquivo ZIP original para a lixeira.
     - Retorna a lista com os arquivos extraídos.
    """
    extracted_files = extract_zip(zip_path, output_dir)
    moved = move_to_trash(zip_path)
    if not moved:
        logger.warning(f" [AVISO] O arquivo ZIP original não foi movido para a lixeira: {zip_path}")
    return extracted_files
