from os import listdir, path, makedirs
from shutil import move
from typing import List, Tuple
import pandas as pd
from config.settings import settings
from pathlib import Path
from .email_extractor import EmailExtractor
from .csv_extractor import CSVExtractor
from common.logging_utils import get_logger

class ExtractManager:
    """
    Gerencia o pipeline da extração.
    1. Baixa arquivos anexados do e-mail (EmailExtractor).
    2. Processa e normaliza arquivos CSV/XLSX (CSVExtractor).
    3. Move arquivos processados da pasta 'incoming' para a pasta 'processed'.
    """

    def __init__(self):
        self.logger = get_logger("extract-manager")
        
        # Inicializa o extrator de e-mail (que baixa arquivos para sua pasta de destino)
        self.email_extractor = EmailExtractor()
        
        # Inicializa o extrator CSV/XLSX. 
        # Ele lê da pasta de destino do EmailExtractor e move para 'incoming' após processar.
        self.csv_extractor = CSVExtractor(
            dir_origem=self.email_extractor.dir_destino,
            dir_destino= Path(settings.DIR_PROCESSED)  # Local onde o CSVExtractor deposita arquivos processados
        )

        # Diretório com os arquivos processados
        self.processed_dir = Path(settings.DIR_PROCESSED)

        # Cria a pasta 'processed' caso não exista.
        makedirs(self.processed_dir, exist_ok=True)
        self.logger.info(f"[INFO] Gerenciador de Extração inicializado. Destino final: {self.processed_dir}")


    def _move_processed_files(self, incoming_dir: str) -> int:
        """Método para mover todos os arquivos da pasta 'incoming' (processados pelo CSVExtractor) para a pasta 'processed'."""
        
        self.logger.info(f"[INFO] Iniciando a movimentação dos arquivos de '{incoming_dir}' para '{self.processed_dir}'.")
        
        arquivos_a_mover = [
            f for f in listdir(incoming_dir) 
            if path.isfile(path.join(incoming_dir, f)) and not f.startswith(".")
        ]
        
        total_moved = 0
        
        for arquivo_nome in arquivos_a_mover:
            caminho_origem = path.join(incoming_dir, arquivo_nome)
            caminho_destino = path.join(self.processed_dir, arquivo_nome)
            
            try:
                move(caminho_origem, caminho_destino)
                self.logger.debug(f"[AVISO] Arquivo movido para 'processed': {arquivo_nome}")
                total_moved += 1
            except Exception as e:
                self.logger.warning(f"[ERRO] Falha ao mover o arquivo {arquivo_nome} para 'processed'. Erro: {e}")

        self.logger.info(f"[STATUS] {total_moved} arquivos movidos de 'incoming' para 'processed'.")
        return total_moved


    def run(self, since_date: str = None) -> List[Tuple[str, pd.DataFrame]]:
        """Método para executar o pipeline de extração completo: e-mail -> CSV/XLSX -> Movimentação."""
        
        self.logger.info("[STATUS] Iniciando o pipeline de extração...")

        # Extrai anexos do e-mail
        arquivos_extraidos = self.email_extractor.extract(since_date=since_date)
        if not arquivos_extraidos:
            self.logger.warning("[AVISO¹] Nenhum arquivo novo extraído do e-mail.")
        else:
            self.logger.info(f"[AVISO²] {len(arquivos_extraidos)} arquivos extraídos do e-mail.")

        # Processa arquivos CSV/XLSX e gera DataFrames
        dataframes = self.csv_extractor.extract()
        if not dataframes:
            self.logger.warning("[AVISO¹] Nenhum DataFrame válido gerado pelo CSV Extractor.")
        else:
            self.logger.info(f"[AVISO²] {len(dataframes)} DataFrames processados e prontos para a Transformação.")

        # Move arquivos processados da pasta 'incoming' para 'processed'
        self._move_processed_files(self.csv_extractor.dir_destino)
        
        self.logger.info(f"[OK] O Pipeline de Extração foi concluído com sucesso! Total de DataFrames construídos: {len(dataframes)}")
        
        return dataframes