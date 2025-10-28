from abc import ABC, abstractmethod
import pandas as pd

class BaseWriter(ABC):
    "Classe do tipo abstrata que servirá de base para escrever em diferentes banco de dados.Todos deverão herdar dessa classe"

    @abstractmethod
    def write(self, df: pd.DataFrame, table_name: str, **kwargs):
        """ 
        A função escreverá o DataFrame em uma tabela no banco de dados (Relacional ou Não Relacional).
        Parâmetro: df - Aponta para os dados a serem gravados.
        Parâmetro: table_name - Nome da tabela ou coleção.
        Parâmetro: kwargs - parâmetros adicionais que forem específicos para cada banco.
        """
        pass
    
    @abstractmethod
    def create_table_if_not_exists(self, table_name: str, df: pd.DataFrame):
        """
        Criará a tabela no banco de dados caso ela não exista.       
        """
        pass