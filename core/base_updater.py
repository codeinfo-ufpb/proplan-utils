from abc import ABC, abstractmethod

class BaseUpdater(ABC):
    "Classe do tipo abstrata que servirá de base para atualização de registros em diferentes banco de dados.Todos deverão herdar dessa classe"


    @abstractmethod
    def update(self, table_name: str, filter_condition: dict, update_values: dict, **kwargs):
        """
        Atualizará os registros em uma tabela ou coleção do banco de dados.
        Parâmetro: table_name - nome da tabela ou coleção.
        Parâmetro: filter_condition - condição para filtrar e localizar os registros a serem atualizados.
        Parâmetro: update_values - valores que serão atualizados.
        Parâmetro: kwargs - parâmetros adicionais que forem específicos para cada banco.
        """
        pass

    @abstractmethod
    def bulk_updates(self, table_name: str, updates: list[dict]):
        """
        Realizará atualizações em quantidades ou lotes. 
        parâmetro: table_name: str - nome da tabela.
        parâmetro: updates - lista de instruções para proceder com a atualização ou atualizações.
        """
        pass