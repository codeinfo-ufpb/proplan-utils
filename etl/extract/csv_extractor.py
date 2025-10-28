import pandas as pd
from os import path, getenv, makedirs, listdir
from shutil import move
from common.logging_utils import get_logger
from core.base_extractor import BaseExtractor

class CSVExtractor(BaseExtractor):
    """ Lê os arquivos CSV/XLSX de uma pasta de origem, processa e normaliza os dados, depois move os arquivos para a pasta de destino (incoming) para demonstrar que foi tratado previamente."""

    def __init__(self, dir_origem=None, dir_destino=None):

        self.logger = get_logger("csv-extractor")
        self.dir_origem = dir_origem or getenv("DIR_EMAILS", "./data/emails")
        self.dir_destino = dir_destino or getenv("DIR_INCOMING", "./data/incoming")

        # Cria a pasta incoming caso não exista.
        makedirs(self.dir_destino, exist_ok=True)

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza os nomes das colunas:
        - Remove espaços extras.
        - Converte para minúsculas.
        - Substitui caracteres especiais como espaços, ponto e - por _ a fim de manter uniformidade.
        """
        df.columns = [
            col.strip().lower().replace(" ", "_").replace(".", "_").replace("-", "_")
            for col in df.columns
        ]
        return df

    def _read_csv_with_auto_sep(self, filepath):
        """
        O método tem como objetivo tentar detectar automaticamente o separador do CSV.
        """
        for sep in [";", ",", "\t"]:
            try:
                df = pd.read_csv(filepath, sep=sep, encoding="utf-8", low_memory=False)
                if len(df.columns) > 1:
                    return df
            except Exception:
                continue
        raise ValueError(f"[AVISO] Não foi possível ler o arquivo CSV: {filepath}")

    def extract(self):
        if not path.exists(self.dir_origem):
            self.logger.error(f"Ops! [ERRO] A Pasta de origem não foi encontrada: {self.dir_origem}")
            return []

        arquivos = [f for f in listdir(self.dir_origem) if not f.startswith(".")]
        dataframes = []

        for arquivo in arquivos:
            caminho_origem = path.join(self.dir_origem, arquivo)
            if not path.isfile(caminho_origem):
                continue

            try:
                if arquivo.lower().endswith(".csv"):
                    df = self._read_csv_with_auto_sep(caminho_origem)
                elif arquivo.lower().endswith((".xls", ".xlsx")):
                    df = pd.read_excel(caminho_origem)
                else:
                    self.logger.info(f"[AVISO] Tipo de arquivo não suportado: {arquivo}")
                    continue

                df = self.validate_dataframe(df)
                df = self._normalize_columns(df)
                self.logger.info(f"[OK] Arquivo carregado e normalizado com sucesso: {arquivo} — {len(df)} linhas.")
                dataframes.append((arquivo, df))

                # Move arquivo para a pasta de destino (incoming)
                caminho_destino = path.join(self.dir_destino, arquivo)
                move(caminho_origem, caminho_destino)
                self.logger.info(f"[INFO] Arquivo movido para a pasta incoming: {arquivo}")

            except Exception as e:
                self.logger.error(f"Ops! [ERRO] Falha ao processar o arquivo. Nome do Arquivo: {arquivo}. Erro: {e}")

        if not dataframes:
            self.logger.warning("[INFO] Nenhum arquivo válido que tenha sido processado.")

        return dataframes
