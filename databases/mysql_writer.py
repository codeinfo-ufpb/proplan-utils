import pandas as pd
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from core.base_writer import BaseWriter 


class MySQLWriter(BaseWriter):
    "Classe específica para escrever no banco de dados MySQL. Permitirá a escrita de Dataframes em tabelas de forma padronizada e segura."

    def __init__(self, connection_string: str):
        """Inicializa o writer com a string de conexão do banco.
        Modelo: mysql+pymysql://user:password@localhost:3306/nome_do_banco
        """

        self.connection_string = connection_string
        self.engine = sqlalchemy.create_engine(self.connection_string)

    def write(self, df: pd.DataFrame, table_name:str, if_exists='append', **kwargs):
        "Escreverá o DataFrame no banco de dados MySQL. Se já existir não permitirá sobrescrever."

        try:
            df.to_sql(table_name, con=self.engine, if_exists=if_exists, index=False, **kwargs)
            print(f"Tabela[OK]: '{table_name}' gravada com sucesso no banco de dados MySQL.")

        except SQLAlchemyError as e:
            print(f"[ERRO] Ops! Tivemos um erro ao carregar os dados para inserir no banco de dados MySQL. Erro:{e}")

    def create_table_if_not_exists(self, table_name: str, df: pd.DataFrame):
        "Criará a tabela automaticamente, caso não exista."

        try:
            inspector = sqlalchemy.inspect(self.engine)
            if not inspector.has_table(table_name):
                df.head(0).to_sql(table_name, con=self.engine, if_exists="fail", index=False)
                print(f"Tabela[OK]: '{table_name}' criada com sucesso.")
            else:
                print(f"[INFO] Tabela: '{table_name} já existe no banco de dados. Nenhuma ação será necessária.")
        
        except SQLAlchemyError as e:
            print(f"[ERRO] Ops! Tivemos um erro ao carregar os dados para criar a tabela '{table_name}' no banco de dados MySQL. Erro:{e}")