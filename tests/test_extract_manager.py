# test_extract_manager.py
from etl.extract.extract_manager import ExtractManager
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

def run_test():
    manager = ExtractManager()

    # Opcional: define desde quando buscar e-mails (ou None para últimos 30 dias)
    since_date = None  # Ex: datetime(2025, 10, 1)

    # Executa pipeline
    dataframes = manager.run(since_date=since_date)

    # Mostra resultados
    if not dataframes:
        print("\n[Nenhum arquivo processado]")
        return

    print(f"\nTotal de arquivos processados: {len(dataframes)}\n")
    for i, (nome_arquivo, df) in enumerate(dataframes, start=1):
        print(f"Arquivo {i} ({nome_arquivo}) - {df.shape[0]} registros, {df.shape[1]} colunas")
        print(df.head(), "\n")  # Exibe primeiras linhas para conferência

    # Lista arquivos ainda presentes na pasta de entrada
    dir_entrada = os.getenv("DIR_DATASA", "./data/emails")
    arquivos_restantes = os.listdir(dir_entrada)
    print(f"Arquivos restantes na pasta de entrada: {arquivos_restantes}")

if __name__ == "__main__":
    run_test()
