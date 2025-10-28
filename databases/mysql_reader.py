import pandas as pd
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from core.base_reader import BaseReader

class MySQLReader(BaseReader):
    "Classe específica para leitura no banco de dados MySQL. Permitirá realizar consultas padronizadas."

    def __init__(self, connection_string: str):
        """Inicializa o reader com a string de conexão do banco.
            Modelo: mysql+pymysql://user:password@localhost:3306/nome_do_banco
        """

        self.connection_string = connection_string
        self.engine = sqlalchemy.create_engine(self.connection_string)

    def read(self, query:str, **kwargs) -> pd.DataFrame:
        "Executará uma query SQL e retornará o resultado em formato DataFrame."

        try:
            df = pd.read_sql(query, con=self.engine, **kwargs)
            print(f"Consulta[OK]: Consulta realizada com sucesso no banco de dados MySQL.")
            return df
        
        except SQLAlchemyError as e:
            print(f"[ERRO] Ops! Tivemos um erro ao realizar a consulta no banco de dados MySQL. Erro:{e}")

    def list_tables(self, **kwargs) -> list:
        "Lista todas as tabelas disponíveis no banco MySQL."

        try:
            inspector = sqlalchemy.inspect(self.engine)
            tables = inspector.get_table_names()
            print(f"[INFO] Tabelas Encontradas: {tables}")
            return tables
        
        except SQLAlchemyError as e:
            print(f"[ERRO] Falha ao listar as tabelas: {e}")
            return[]
        
