from os import listdir, path, makedirs
from datetime import datetime
from shutil import move
from .email_extractor import EmailExtractor
from .csv_extractor import CSVExtractor
from common.logging_utils import get_logger

class ExtractManager:
    """Gerencia o pipeline da extração: Baixa arquivos do e-mail (EmailExtractor). Processa arquivos CSV/XLSX (CSVExtractor). Move arquivos processados para pasta processed"""

    def __init__(self):
        self.logger = get_logger("extract-manager")
        self.email_extractor = EmailExtractor()
        self.csv_extractor = CSVExtractor(
            dir_origem=self.email_extractor.dir_destino,
            dir_destino="./data/incoming"
        )
        self.processed_dir = "./data/processed"

        # Cria a pasta processed caso não exista.
        makedirs(self.processed_dir, exist_ok=True)

    def run(self, since_date=None):
        self.logger.info("[STATUS] Iniciando o pipeline de extração...")

        """
        Realiza o gerenciamento do pipeline desde a extração do e-mail até o envio para pasta processados. A orquestração ocorre:
        
        """

        # Extrai anexos do e-mail
        arquivos_extraidos = self.email_extractor.extract(since_date=since_date)
        if not arquivos_extraidos:
            self.logger.warning("[INFO] Nenhum arquivo extraído do e-mail.")
        else:
            self.logger.info(f"[OK] {len(arquivos_extraidos)} arquivos extraídos do e-mail.")

        # Processa arquivos CSV/XLSX
        dataframes = self.csv_extractor.extract()
        if not dataframes:
            self.logger.warning("[INFO] Nenhum DataFrame gerado pelo CSV Extractor.")
        else:
            self.logger.info(f"[OK] {len(dataframes)} DataFrames processados pelo CSV Extractor.")

        # Move arquivos processados de incoming para processed
        arquivos_incoming = [
            path.join(self.csv_extractor.dir_destino, f)
            for f in listdir(self.csv_extractor.dir_destino)
            if path.isfile(path.join(self.csv_extractor.dir_destino, f))
        ]

        for arquivo in arquivos_incoming:
            try:
                move(arquivo, path.join(self.processed_dir, path.basename(arquivo)))
                self.logger.info(f"[OK] Arquivos processados. Todos os arquivos foram movidos para a pasta: processed. {path.basename(arquivo)}")
            except Exception as e:
                self.logger.warning(f"[AVISO] Tivemos uma falha ao mover o arquivo para processed: {arquivo}. Erro: {e}")

        self.logger.info(f"[OK] O Pipeline foi concluído com sucesso! Total de DataFrames construídos: {len(dataframes)}")
        return dataframes
