from etl.extract.email_extractor import EmailExtractor
from dotenv import load_dotenv
from config.settings import settings
import os

load_dotenv()  # carrega .env

def run_test():
    extractor = EmailExtractor()
    arquivos = extractor.extract()  # opcional: year=2025, month=10
    print("Arquivos retornados pela extração:", arquivos)
    print("Arquivos no diretório:", os.listdir(os.getenv("DIR_DATASA", settings.DIR_RAW_EMAIL)))

if __name__ == "__main__":
    run_test()
