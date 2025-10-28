from abc import ABC, abstractmethod
import pandas as pd
from common.logging_utils import get_logger


class BaseTransformer(ABC):
    """
    Classe abstrata responsável pela transformação de dados.
    Todos os transformadores (CSV, XLSX, JSON, API etc) deverão herdar
    esta classe para garantir padronização, consistência e fácil manutenção.
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__.lower())

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Método abstrato que deverá ser implementado por cada transformador.
        Deve receber um DataFrame e retornar outro DataFrame transformado.
        """
        pass

    def validate_input(self, df: pd.DataFrame):
        """
        Valida se o DataFrame de entrada é válido e não está vazio.
        """
        if df is None or df.empty:
            self.logger.error("[ERRO] O DataFrame de entrada está vazio ou nulo.")
            raise ValueError("[ERRO] O DataFrame de entrada está vazio ou nulo.")
        return True
    

    def validate_output(self, df: pd.DataFrame):
        """
        Valida se o DataFrame transformado é válido antes de ser retornado.
        """
        if df is None or df.empty:
            self.logger.error("[ERRO] O DataFrame transformado está vazio ou inválido.")
            raise ValueError("[ERRO] O DataFrame transformado está vazio ou inválido.")
        return True

    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executa a transformação completa com validações e logging.
        """
        self.logger.info("[STATUS] Iniciando transformação de dados...")
        self.validate_input(df)
        transformed_df = self.transform(df)
        self.validate_output(transformed_df)
        self.logger.info("[OK] Transformação concluída com sucesso.")
        return transformed_df
    
    
