# test_email_extractor.py
from etl.extract.email_extractor import EmailExtractor
from dotenv import load_dotenv
import os

load_dotenv()  # carrega .env

def run_test():
    extractor = EmailExtractor()
    arquivos = extractor.extract()  # opcional: year=2025, month=10
    print("Arquivos retornados pela extração:", arquivos)
    print("Arquivos no diretório:", os.listdir(os.getenv("DIR_DATASA", "./data/emails")))

if __name__ == "__main__":
    run_test()
