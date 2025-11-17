import pandas as pd
import numpy as np
from os import path, makedirs, listdir
from pathlib import Path
from config.settings import settings
from shutil import move
from common.logging_utils import get_logger
from core.base_extractor import BaseExtractor

class CSVExtractor(BaseExtractor):
    """ Classe que lê os arquivos CSV/XLSX de uma pasta de origem, processa e normaliza os dados, 
        depois move os arquivos para a pasta de destino que será em tratamento ou aguardando (incoming) para demonstrar que foi tratado previamente."""
    

    def __init__(self, dir_origem=None, dir_destino=None):

        self.logger = get_logger("csv-extractor")

        # Garante que a classe Base do extrator tenha acesso ao logger, se necessário
        self.BaseExtractor_logger = self.logger 

        self.dir_origem = Path(settings.DIR_RAW_EMAIL)
        self.dir_destino = Path(settings.DIR_INCOMING)

        # Cria a pasta incoming caso não exista.
        makedirs(self.dir_destino, exist_ok=True)
        self.logger.info(f"[INFO] Pasta de destino ('incoming') verificada/criada em: {self.dir_destino}")
    
    def _read_csv_with_auto_sep(self, filepath: str) -> pd.DataFrame:
        """
        Método para detectar automaticamente o separador do CSV e o encoding correto. Este é o método de FALLBACK para CSVs simples.
        """
        # Tenta os encodings mais comuns
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"] 
        # Tenta os separadores mais comuns
        separators = ["\t", ";", ",", "|"]

        for sep in separators:
            for enc in encodings:
                try:
                    df = pd.read_csv(filepath, sep=sep, encoding=enc, low_memory=False)
                    # Verifica se o DataFrame tem mais de uma coluna (indicando sucesso na detecção do separador)
                    if len(df.columns) > 1:
                        self.logger.info(f"[OK] Arquivo lido (Fallback Automático): Separador: '{sep}' | Encoding: {enc}")
                        return df
                except Exception as e:
                    self.logger.debug(f"[AVISO] Tentativa falha para {filepath} com sep='{sep}', enc='{enc}': {e}")
                    continue

        raise ValueError(f"[ERRO] Não foi possível ler o arquivo CSV: {filepath} com os separadores e encodings testados. Reveja o tipo de codificação do CSV ou o Separador!")

    def _read_complex_csv(self, filepath: str) -> pd.DataFrame | None:
        """
        Método para ler arquivos csv considerados complexos (Por exemplo: cabeçalho na linha 3, dados na linha 5).
        Tenta listas com os encodings prováveis ("latin-1", "cp1252", "ISO-8859-1", "utf-16") e com os separadores padrões.
        Retorna o DataFrame se for bem-sucedido ou nada se falhar.
        """
        # Tenta com encodings conhecidos para arquivos PT-BR tabulados
        complex_encodings = ["latin-1", "cp1252", "ISO-8859-1", "utf-16"] 
        sep = ["\t", ";", ",", "|"]
        
        for enc in complex_encodings:
            self.logger.info(f"[INFO] Tentativa Complexa: sep='{sep}', enc='{enc}'.")
            try:
                # Leitura bruta sem cabeçalho para obter todas as linhas
                df_temp = pd.read_csv(filepath, sep=sep, encoding=enc, header=None, low_memory=False)
                
                # Checagem mínima referente às linhas. Exemplo: 5.
                if len(df_temp.index) < 5:
                    self.logger.debug(f"[AVISO] Arquivo muito curto para o padrão complexo. Vá para o próximo encoding ou fallback.")
                    continue

                # Definição da linha 3 (índice 2) onde contém as colunas principais.
                header_row = df_temp.iloc[2] 
                
                # Os dados começam na linha 5 (índice 4)
                df = df_temp.iloc[4:].copy()
                
                # Aplicar o cabeçalho e tratar NaN
                df.columns = [str(col) if pd.notna(col) else f'Unnamed:{i}' for i, col in enumerate(header_row)]
                
                # Uma verificação básica de sucesso (se o cabeçalho foi aplicado corretamente)
                if len(df.columns) < 5:
                     self.logger.debug("[AVISO] Leitura complexa retornou poucas colunas. Falhando para fallback.")
                     continue

                self.logger.info(f"[OK] CSV complexo lido com sucesso pela lógica dedicada ({enc}). {len(df)} linhas de dados.")
                return df

            except Exception as e:
                self.logger.debug(f"[AVISO] Tentativa complexa com '{enc}' falhou. Motivo: {e}.")
                continue # Tenta o próximo encoding

        # Se falhou em todos os encodings conhecidos, retorna None
        return None
    
    def extract(self) -> list[tuple[str, pd.DataFrame]]:
        """Método principal para extração. Lê arquivos CSV/XLSX da pasta de origem, normaliza, valida e move para a pasta de destino (Itens Processados)"""

        if not path.exists(self.dir_origem):
            self.logger.error(f"[ERRO] A Pasta de origem não foi encontrada: {self.dir_origem}. Extração abortada.")
            return []
        
        # Lista apenas arquivos que não são ocultos
        arquivos = [f for f in listdir(self.dir_origem) if path.isfile(path.join(self.dir_origem, f)) and not f.startswith(".")]
        self.logger.info(f"[INFO] Encontrados {len(arquivos)} arquivo(s) na pasta de origem ({self.dir_origem}).")
        dataframes = []

        for arquivo in arquivos:
            caminho_origem = path.join(self.dir_origem, arquivo)
            df = None # Inicializa df para o escopo do bloco try/except

            if not path.isfile(caminho_origem):
                continue

            try:
                # --- TRATAMENTO PARA ARQUIVOS CSV ---
                if arquivo.lower().endswith((".csv")):
                    
                    # TENTA LER COM A LÓGICA COMPLEXA DEDICADA
                    df = self._read_complex_csv(caminho_origem)

                    if df is None:
                        # SE A LEITURA COMPLEXA FALHAR, USA O FALLBACK DE DETECÇÃO AUTOMÁTICA
                        self.logger.info(f"[INFO] Aplicando fallback: Lendo CSV com detecção automática de separador (Método Padrão).")
                        df = self._read_csv_with_auto_sep(caminho_origem)
                
                # TRATAMENTO PARA ARQUIVOS XLSX/XLS
                elif arquivo.lower().endswith((".xls", ".xlsx")):
                    self.logger.info(f"[INFO] Lendo Excel/XLSX/XLS. Tentativa 1: cabeçalho na linha 3 (índice 2)... Parametrizado por observação")
                    
                    df_temp = pd.read_excel(caminho_origem, header=None, engine='openpyxl')
                    
                    # Pegamos a linha 3 (índice 2) como cabeçalho. Ajustável de acordo com a realidade de observação do arquivo.
                    header_row = df_temp.iloc[2]
                    
                    # Usamos a linha 4 (índice 3) em diante como dados. Ajustável de acordo com a realidade de observação do arquivo.
                    df = df_temp[3:].copy()
                    
                    # Damos o nome do cabeçalho
                    df.columns = [str(col) if pd.notna(col) else f'Unnamed:{i}' for i, col in enumerate(header_row)]
                    
                    self.logger.info(f"[OK] Excel lido com cabeçalho da linha 3. Colunas setadas manualmente.")
                
                else:
                    self.logger.info(f"[AVISO] Tipo de arquivo não suportado: {arquivo}")
                    continue

                # --- PROCESSAMENTO ÚNICO APÓS LEITURA BEM-SUCEDIDA ---
                
                # Verificação básica de DF
                if df is None or len(df.columns) == 0:
                     raise ValueError("O leitor de arquivo (CSV/XLSX) retornou um DataFrame vazio/nulo ou sem colunas.")

                # Validação (chamado do BaseExtractor)
                df = self.validate_dataframe(df)
                
                # Normalização das Colunas, manter comentado pois se for necessário mudamos.
                # df = self._normalize_columns(df)
                
                if len(df) == 0:
                    self.logger.warning(f"[AVISO] O DataFrame resultante para {arquivo} está vazio após validação/limpeza e será ignorado.")
                    continue 
                
                self.logger.info(f"[OK] Arquivo carregado e normalizado com sucesso: {arquivo} — {len(df)} linhas.")
                dataframes.append((arquivo, df))

                # Move arquivo para a pasta de destino (incoming)
                caminho_destino = path.join(self.dir_destino, arquivo)
                move(caminho_origem, caminho_destino)
                self.logger.info(f"[INFO] Arquivo movido para a pasta incoming: {arquivo}")

            except Exception as e:
                self.logger.error(f"[ERRO] Falha ao processar o arquivo. Nome do Arquivo: {arquivo}. Erro: {e}")

        if not dataframes:
            self.logger.warning("[INFO] Nenhum arquivo válido que tenha sido processado.")

        return dataframes