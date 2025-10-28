import psycopg2
import pandas as pd
from .base_writer import BaseWriter


class PostgresWriter(BaseWriter):
    "Classe específica para escrever no banco de dados Postgres. Permitirá a escrita de Dataframes em tabelas de forma padronizada e segura."
    