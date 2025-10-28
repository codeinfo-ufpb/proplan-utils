import os
import pandas as pd
from common.logging_utils import get_logger
from core.base_transformer import BaseTransformer
from shutil import move

class CSVTransformer(BaseTransformer):
    """Classe responsável por aplicar as transformações e padronizações em arquivos CSV ou XLSX já processados pela etapa de extração. Os arquivos devem estar localizados em data/processed."""

    def __init__(self, input_dir: str = "./data/processed", output_dir: str = "./data/transformed"):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logger = get_logger("csv-transformer")

    def transform_text_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove espaços extras, normaliza texto e padroniza colunas. Double Check apenas para evitar eventuais erros.
        """
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(" ", "_").str.replace("-", "_").str.lower()
        df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))
        return df

    def convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converte os tipos de colunas automaticamente quando aplicável.
        """
        # Converter colunas de data
        for col in df.columns:
            if "data" in col or "date" in col or "dt" in col:
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce", format=None)
                except Exception:
                    pass

        # converter colunas numéricas
        for col in df.select_dtypes(include=['object']).columns:
            try:
                df[col] = pd.to_numeric(df[col].str.replace(",", "."), errors="ignore")
            except Exception:
                continue
        return df

    def map_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica mapeamentos personalizados em colunas específicas. Neste exemplo estamos tratando sobre licitações.
        """
        mapping = {
            'CD': 'Compra Direta',
            'PE': 'Pregão Eletrônico',
            'CV': 'Convite',
            'PP': 'Pregão Presencial',
            'IN': 'Inexigibilidade',
            'CC': 'Concorrência',
        }

        if 'tipo' in df.columns:
            df['tipo'] = df['tipo'].replace(mapping)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executará todas as transformações.
        """
        self.logger.info("[INFO] Iniciando transformações básicas...")
        df = self.transform_text_columns(df)
        df = self.convert_types(df)
        df = self.map_values(df)
        df.dropna(how="all", inplace=True)
        self.logger.info(f"[OK] Transformações aplicadas. Shape final: {df.shape}")
        return df

    def load_file(self, filename: str) -> pd.DataFrame:
        """
        Carregará o arquivo CSV ou XLSX da pasta processed. Para a pasta load.
        """
        file_path = os.path.join(self.input_dir, filename)
        if not os.path.exists(file_path):
            self.logger.error(f"Ops! [ERRO] Arquivo não encontrado: {file_path}")
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        self.logger.info(f"[STATUS] Carregando arquivo..: {file_path}")
        try:
            if filename.lower().endswith('.csv'):
                df = pd.read_csv(file_path, encoding="utf-8", sep=";", engine='python')
            elif filename.lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"[AVISO] Formato não suportado: {filename}")
        except Exception as e:
            self.logger.error(f"Ops! [ERRO] Falha ao carregar arquivo. Nome do Arquivo: {filename}: {e}")
            raise

        self.validate_input(df)
        self.logger.info(f"[OK] Arquivo carregado. Shape: {df.shape}")
        return df

    def transform_file(self, filename: str) -> pd.DataFrame:
        """
        Executa o processo completo de transformação e move o arquivo para transformed.
        """
        df = self.load_file(filename)
        df_transformed = self.execute(df)

        # Cria a pasta caso não exista. Garantirá que a pasta de saída existe
        os.makedirs(self.output_dir, exist_ok=True)

        src_path = os.path.join(self.input_dir, filename)
        dest_path = os.path.join(self.output_dir, filename)

        try:
            move(src_path, dest_path)
            self.logger.info(f"[OK] Arquivo original movido para: {dest_path}")
        except Exception as e:
            self.logger.error(f"Ops! [ERRO] Falha ao mover arquivo: {e}")

        return df_transformed
