from abc import ABC, abstractmethod
import pandas as pd


class BaseExtractor(ABC):
    """
    Classe abstrata responsável pela extração de dados.
    Todos os extratores (API, CSV, XLSX, JSON, XML etc) deverão herdar
    esta classe para garantir padronização e facilitar a manutenção.
    """

    @abstractmethod
    def extract(self, *args, **kwargs) -> pd.DataFrame:
        """
        Método abstrato que deverá ser implementado por cada extrator.
        Deve retornar um DataFrame contendo os dados extraídos.
        """
        pass

    def validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida se o DataFrame retornado é válido e não está vazio.
        """
        if df is None or df.empty:
            raise ValueError(
                "[ERRO] O DataFrame está vazio ou nulo. Nenhum dado foi extraído."
            )
        return df
