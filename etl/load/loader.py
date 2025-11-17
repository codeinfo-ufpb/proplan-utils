import pandas as pd
import os
import glob
from pathlib import Path
from datetime import datetime
import logging
import re
from typing import List, Dict, Any, Optional, Tuple

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('datalake-loader')

class DatalakeLoader:
    """
    Responsável por ler arquivos do diretório de Staging (CSV/Excel),
    aplicar transformações de particionamento e salvar como Parquet no Datalake.
    """

    def __init__(self):
        # Diretórios lidos das variáveis de ambiente
        self.staging_dir = Path(os.getenv("DATALAKE_STAGING_DIR", "data/transformed"))
        self.output_dir = Path(os.getenv("DATALAKE_OUTPUT_DIR", "data/datalake"))
        
        logger.info(f"[INFO] Diretório de destino do Datalake: {self.output_dir}")

    def _read_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """Lê um arquivo CSV ou Excel e retorna um DataFrame."""
        if file_path.suffix.lower() == '.csv':
            try:
                # Tenta ler CSV com encoding UTF-8, que é o padrão mais comum
                return pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                # Tenta ISO-8859-1 (Latin-1) se UTF-8 falhar
                return pd.read_csv(file_path, encoding='iso-8859-1')
            except Exception as e:
                logger.error(f"[ERRO] Falha ao ler CSV {file_path.name}: {e}")
                return None
        
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            try:
                return pd.read_excel(file_path)
            except Exception as e:
                logger.error(f"[ERRO] Falha ao ler Excel {file_path.name}: {e}")
                return None
        
        else:
            logger.warning(f"[AVISO] Formato de arquivo não suportado: {file_path.name}")
            return None

    def _prepare_data_for_parquet(self, df: pd.DataFrame, dataset_name: str) -> Optional[pd.DataFrame]:
        """
        Prepara o DataFrame:
        1. Remove colunas de metadados indesejadas (e.g., 'Unnamed: X').
        2. Garante a conversão de colunas 'object' para strings para evitar erros do PyArrow.
        3. Cria colunas de particionamento 'ano' e 'mes' se 'data_base' existir.
        """
        
        # 1. Limpeza de colunas 'Unnamed: X' que causam erros de tipos mistos
        cols_to_drop = [col for col in df.columns if col.startswith('Unnamed:')]
        if cols_to_drop:
            df.drop(columns=cols_to_drop, inplace=True)
            logger.info(f"[INFO] Dataset '{dataset_name}': Removidas colunas de metadados: {cols_to_drop}")

        # 2. Coerção de tipos: Converte todas as colunas 'object' para strings
        # O erro "Expected bytes, got a 'int' object" ocorre quando 'object' contém tipos mistos.
        for col in df.select_dtypes(include=['object']).columns:
            try:
                # Converte para string e substitui NaN por string vazia para consistência
                df[col] = df[col].astype(str).fillna('')
            except Exception as e:
                logger.warning(f"[AVISO] Dataset '{dataset_name}': Falha ao forçar tipo str na coluna '{col}': {e}")
                
        # 3. Criação de colunas de particionamento se 'data_base' existir
        if 'data_base' in df.columns:
            try:
                # Converte a coluna para datetime
                df['data_base'] = pd.to_datetime(df['data_base'], errors='coerce')
                # Remove linhas onde a conversão falhou
                df.dropna(subset=['data_base'], inplace=True)

                if not df.empty:
                    df['ano'] = df['data_base'].dt.year
                    df['mes'] = df['data_base'].dt.month
                    # Converte ano/mes para int para particionamento correto
                    df['ano'] = df['ano'].astype(int)
                    df['mes'] = df['mes'].astype(int)
                    logger.info(f"[INFO] Dataset '{dataset_name}': Colunas 'ano' e 'mes' criadas para particionamento.")
                
            except Exception as e:
                logger.error(f"[ERRO] Falha na criação de partições para '{dataset_name}': {e}")
                return None
        else:
            logger.warning(f"[AVISO] Dataset '{dataset_name}': Coluna 'data_base' não encontrada. Particionamento não será aplicado.")
            
        return df

    def _save_to_parquet(self, df: pd.DataFrame, dataset_name: str) -> Optional[Path]:
        """Salva o DataFrame no formato Parquet, aplicando particionamento se possível."""
        
        if df.empty:
            logger.warning(f"[AVISO] DataFrame vazio para o dataset '{dataset_name}'. Pulando a escrita.")
            return None

        # Cria o nome do arquivo único (incluindo timestamp)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{dataset_name}_{timestamp}.parquet"
        
        # Caminho do diretório de destino (e.g., data/datalake/vendas_transformadas)
        dataset_path = self.output_dir / dataset_name
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        partition_cols = []
        if 'ano' in df.columns and 'mes' in df.columns:
            partition_cols = ['ano', 'mes']
            
        try:
            if partition_cols:
                # Salva com particionamento no diretório do dataset
                logger.info(f"[INFO] Iniciando carga Parquet particionada por {partition_cols} para '{dataset_name}' em: {dataset_path}")
                
                # PyArrow lida com a escrita eficiente de Parquet e particionamento
                df.to_parquet(
                    dataset_path,
                    engine='pyarrow',
                    index=False,
                    partition_cols=partition_cols
                )
                logger.info(f"[SUCESSO] Carga Parquet particionada concluída para '{dataset_name}'.")

            else:
                # Salva como um único arquivo Parquet se não houver colunas de partição
                final_file_path = dataset_path / file_name
                logger.info(f"[INFO] Iniciando carga Parquet simples para '{dataset_name}' em: {final_file_path}")
                
                df.to_parquet(
                    final_file_path,
                    engine='pyarrow',
                    index=False
                )
                logger.info(f"[SUCESSO] Carga Parquet simples concluída para '{dataset_name}'.")
                
            return dataset_path
            
        except Exception as e:
            logger.error(f"[ERRO] Falha na carga Parquet para {dataset_name}: {e}", exc_info=True)
            return None

    def load(self) -> List[Path]:
        """
        Inicia o processo de carga, lendo todos os arquivos no diretório de Staging.
        Retorna uma lista de Paths dos diretórios de datasets carregados com sucesso.
        """
        
        if not self.staging_dir.exists():
            logger.warning(f"[AVISO] Diretório de Staging não encontrado: {self.staging_dir}")
            return []
            
        processed_datasets = []
        
        # Busca por arquivos CSV e Excel
        file_patterns = ['*.csv', '*.xlsx', '*.xls']
        staging_files = []
        for pattern in file_patterns:
            staging_files.extend(list(self.staging_dir.glob(pattern)))

        if not staging_files:
            logger.info("[INFO] Nenhum arquivo CSV/Excel encontrado no diretório de Staging.")
            return []

        for file_path in staging_files:
            dataset_name = file_path.stem # Nome do arquivo sem extensão
            logger.info(f"\n[PROCESSANDO] Iniciando processamento do arquivo: {file_path.name}")
            
            # 1. Leitura
            df = self._read_file(file_path)
            if df is None or df.empty:
                logger.error(f"[ERRO] Pulando {file_path.name} devido a falha na leitura ou estar vazio.")
                continue

            # 2. Preparação (Limpeza e Particionamento)
            df_prepared = self._prepare_data_for_parquet(df, dataset_name)
            if df_prepared is None or df_prepared.empty:
                logger.error(f"[ERRO] Pulando {file_path.name} devido a falha na preparação ou estar vazio após limpeza.")
                continue

            # 3. Escrita no Datalake
            output_path = self._save_to_parquet(df_prepared, dataset_name)
            if output_path:
                processed_datasets.append(output_path)
                
        logger.info("\n--- FIM DA EXECUÇÃO DO DATALAKE LOADER ---")
        return processed_datasets