# test_csv_extractor.py
from etl.extract.csv_extractor import CSVExtractor
from dotenv import load_dotenv
import os

load_dotenv()  # carrega variáveis do .env

def run_test():
    # Caminho da pasta onde os arquivos baixados pelo EmailExtractor estão
    dir_or_files = os.getenv("DIR_DATASA", "./data/emails")

    extractor = CSVExtractor(dir_or_files)
    dataframes = extractor.extract()  # retorna lista de DataFrames

    print(f"\nTotal de arquivos processados: {len(dataframes)}")
    for i, (arquivo, df) in enumerate(dataframes, start=1):
        print(f"\nArquivo {i} ({arquivo}) - {df.shape[0]} registros, {df.shape[1]} colunas")
        print(df.head())  # mostra as 5 primeiras linhas

if __name__ == "__main__":
    run_test()
