from abc import ABC, abstractmethod
import pandas as pd

class BaseReader(ABC):
    "Classe que servirá de base para leitura ou consulta de dados em diferentes banco de dados.Todos deverão herdar dessa classe."

    @abstractmethod
    def read(self, query: str, **kwargs) -> pd.DataFrame:
        """
        Executará uma consulta SQL ou equivalente nos casos NoSQL e retornará um DataFrame.
        Parâmetro: query - comando de consulta SQL ou NoSQL, pipeline etc.
        Parâmetro: kwargs - parâmetros adicionais que forem específicos para cada banco.
        Retornará um DataFrame
        """
        pass

    @abstractmethod
    def list_tables(self, **kwargs) -> list:
        "Listará todas as tabelas ou coleções."
        pass