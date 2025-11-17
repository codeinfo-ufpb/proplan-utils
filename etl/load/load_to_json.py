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


def harmonize_column_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Harmoniza cabeçalhos duplicados e substitui 'Unnamed' pelos nomes válidos da última coluna conhecida.
    Exemplo: 'Unnamed: 4' -> 'Resultado Primário Lei: 4'
    """
    new_columns = []
    last_valid = None

    for col in df.columns:
        col_str = str(col).strip()

        # Se for uma coluna "unnamed", herdamos o nome anterior
        if col_str.lower().startswith("unnamed"):
            if last_valid:
                num = ''.join(filter(str.isdigit, col_str))
                col_str = f"{last_valid}: {num}" if num else last_valid
            else:
                col_str = "Coluna_Sem_Titulo"
        else:
            last_valid = col_str

        new_columns.append(col_str)

    df.columns = new_columns
    logger.info(f"[OK] Cabeçalhos harmonizados ({len(new_columns)} colunas processadas).")
    return df


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
                    df = pd.read_csv(file, sep=",", encoding="latin-1")
                else:  # .xlsx
                    df = pd.read_excel(file, header=2)

                if df.empty:
                    logger.warning(f"[AVISO] Arquivo vazio: {file}")
                    continue

                # 🧩 Harmoniza e limpa cabeçalhos
                df = harmonize_column_headers(df)
                df.columns = [str(c).strip() for c in df.columns]

                # Cria nome do arquivo JSON
                json_file = load_dir / f"{file.stem}.json"

                # Salva em JSON
                df.to_json(json_file, orient="records", date_format="iso", force_ascii=False)
                logger.info(f"[OK] Arquivo convertido para JSON: {json_file}")

            except Exception as e:
                logger.error(f"Ops! [ERRO] Falha ao processar {file}: {e}")


if __name__ == "__main__":
    load_to_json()
