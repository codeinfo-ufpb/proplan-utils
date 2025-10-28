import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from core.base_updater import BaseUpdater

class MySQLUpdater(BaseUpdater):
    "Classe específica para atualizar dados no banco de dados MySQL. Permitirá atualizar de forma padronizada e segura."

    def __init__(self, connection_string: str):
        "Inicializa o updater com a string de conexão do banco."

        self.connection_string = connection_string
        self.engine = sqlalchemy.create_engine(self.connection_string)

    def update(self, table_name: str, filter_condition: dict, update_values: dict, **kwargs):
        "Atualizará os registros em uma tabela do MySQL com base em filtros e novos valores."

        try: 
            where_clause = " AND ".join([f"{k} = '{v}'" for k, v in filter_condition.items()])
            set_clause = " , ".join([f"{k} = '{v}'" for k, v in update_values.items()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause};"

            with self.engine.begin() as conn:
                conn.execute(sqlalchemy.text(query))
                print(f"[OK] Registros atualizados com sucesso. Tabela: '{table_name}'.")
        except SQLAlchemyError as e:
            print(f"[ERRO] Ops! Falha ao atualizar os registros: {e}")

    def bulk_updates(self, table_name: str, updates: list[dict]):
        """ Atualizará múltiplos registros em sequência. Será esperado uma lista de dicionários com filtros e valores. 
            [
                {'filter': {'id': 1}, 'values': {'status': 'ativo'}},
                {'filter': {'id': 2}, 'values': {'status': 'inativo'}}
            ]
        """
        try:
            for u in updates:
                self.update(table_name, u['filter'], u['values'])
                print(f"[OK] Atualizações em lote concluídas com sucesso.")
        except Exception as e:
            print(f"[ERRO] Ops! Tivemos uma Falha na atualização em lote: {e}")
