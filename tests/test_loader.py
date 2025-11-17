import os
import sys
from pathlib import Path
from datetime import datetime
from common.logging_utils import get_logger


logger = get_logger("test-loader")



# --- Configuração de Path e Imports ---
# Adiciona o diretório raiz do projeto ao path para importar módulos
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print(f"[DEBUG] Diretório raiz do projeto: {project_root}")

try:
    # A classe DatalakeLoader está em load/loader.py (assumindo load/loader.py)
    from etl.load.loader import DatalakeLoader
    print("[SETUP] DatalakeLoader importado com sucesso.")
except ImportError as e:
    print(f"[ERRO FATAL] Falha ao importar DatalakeLoader. Verifique o caminho e a instalação do PyArrow. Erro: {e}")
    sys.exit(1)

# --- Variáveis de Execução (Conforme a requisição do usuário) ---
# O Loader lerá os arquivos desta pasta
STAGING_INPUT_DIR = project_root / "data" / "transformed"
# O Loader salvará os arquivos Parquet nesta pasta (será persistente)
PARQUET_OUTPUT_DIR = project_root / "data" / "data_to_parquet_"

def setup_execution_environment():
    """Configura o ambiente com os diretórios reais de Staging e Output."""
    
    # 1. Configura o Diretório de Staging (INPUT)
    print(f"[SETUP] Definindo DATALAKE_STAGING_DIR (INPUT): {STAGING_INPUT_DIR}")
    os.environ["DATALAKE_STAGING_DIR"] = str(STAGING_INPUT_DIR)

    # 2. Configura o Diretório de Output (OUTPUT)
    print(f"[SETUP] Definindo DATALAKE_OUTPUT_DIR (OUTPUT): {PARQUET_OUTPUT_DIR}")
    os.environ["DATALAKE_OUTPUT_DIR"] = str(PARQUET_OUTPUT_DIR)
    
    # Garante que o diretório de output exista (o usuário deseja que ele seja persistente)
    PARQUET_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Verificação de existência da pasta de INPUT
    if not STAGING_INPUT_DIR.exists():
        print(f"[ALERTA] O diretório de Staging (INPUT) '{STAGING_INPUT_DIR}' não existe. Criando-o.")
        print("[AVISO] Certifique-se de que há arquivos CSV/Excel dentro desta pasta antes de rodar.")
        STAGING_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"[INFO] Ambiente pronto. Arquivos serão lidos de '{STAGING_INPUT_DIR.relative_to(project_root)}' e salvos em '{PARQUET_OUTPUT_DIR.relative_to(project_root)}'.")

def execute_loader():
    """Executa o processo de carga do Staging para o Datalake Parquet."""
    
    loader = DatalakeLoader()
    
    print("\n--- INICIANDO EXECUÇÃO: Carga de Staging (CSV/Excel) para Parquet ---")
    
    try:
        # A função load() agora usa os paths reais definidos pelas variáveis de ambiente
        output_paths = loader.load()
        
        # --- Verificação e Relatório ---
        if output_paths:
            print(f"\n[SUCESSO] Processo de carga concluído. {len(output_paths)} datasets processados com sucesso.")
            print("Arquivos Parquet (datasets) foram gerados nas seguintes pastas:")
            for path in output_paths:
                # O path retornado é o diretório do dataset (e.g., .../data_to_parquet_/vendas_transformadas)
                print(f"  -> {Path(path).relative_to(project_root)}")
            
            print(f"\n[OUTPUT] Os dados foram salvos persistentemente em: {PARQUET_OUTPUT_DIR.relative_to(project_root)}")

        else:
            print(f"\n[AVISO] Processo de carga concluído. Nenhum arquivo válido foi encontrado ou processado com sucesso no diretório de Staging: {STAGING_INPUT_DIR.relative_to(project_root)}")

    except Exception as e:
        print(f"\n[ERRO DE EXECUÇÃO] Ocorreu uma falha crítica durante a execução do DatalakeLoader:")
        print(f"Detalhes do Erro: {e}")
        sys.exit(1)


# --- Execução Principal ---
if __name__ == "__main__":
    setup_execution_environment()
    execute_loader()