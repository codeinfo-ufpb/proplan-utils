import sys
import os
from pathlib import Path
import pandas as pd

# Adiciona a raiz do projeto ao sys.path para encontrar 'common'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from common.logging_utils import get_logger

logger = get_logger("json-loader")


transformed_dir = Path("./data/transformed")
load_dir = Path("./etl/load")

 # cria a pasta se não existir
load_dir.mkdir(parents=True, exist_ok=True) 

def load_to_json():
    """
    Converte arquivos transformados (CSV ou XLSX) em JSON e salva na pasta load.
    """
    if not transformed_dir.exists():
        logger.error(f"Ops! [ERRO] Pasta de arquivos transformados não encontrada: {transformed_dir}")
        return

    for file in transformed_dir.iterdir():
        if file.suffix.lower() in [".csv", ".xlsx"]:
            try:
                logger.info(f"[STATUS] Carregando arquivo: {file}")

                # Leitura do arquivo
                if file.suffix.lower() == ".csv":
                    df = pd.read_csv(file, sep=";", encoding="utf-8")
                else:  # .xlsx
                    df = pd.read_excel(file)

                if df.empty:
                    logger.warning(f"[AVISO] Arquivo vazio: {file}")
                    continue

                # Cria nome do arquivo JSON
                json_file = load_dir / f"{file.stem}.json"

                # Salva em JSON
                df.to_json(json_file, orient="records", date_format="iso", force_ascii=False)
                logger.info(f"[OK] Arquivo convertido para JSON: {json_file}")

            except Exception as e:
                logger.error(f"Ops! [ERRO] Falha ao processar {file}: {e}")

if __name__ == "__main__":
    load_to_json()