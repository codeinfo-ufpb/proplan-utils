import os
import pandas as pd
from etl.transform import CSVTransformer
from common.logging_utils import get_logger

logger = get_logger("test-transformer")

# Pastas
processed_dir = "./data/processed"
transformed_dir = "./data/transformed"

# Criar pastas se não existirem
os.makedirs(processed_dir, exist_ok=True)
os.makedirs(transformed_dir, exist_ok=True)

# --- Criar arquivos de teste ---
csv_test_file = os.path.join(processed_dir, "test_data.csv")
xlsx_test_file = os.path.join(processed_dir, "test_data.xlsx")

# CSV de teste
df_csv = pd.DataFrame({
    "nome": ["Sullivan", "Lima", None],
    "data": ["2025-10-24", "2025/10/23", "24-10-2025"],
    "valor": [100.5, None, 300.0]
})
df_csv.to_csv(csv_test_file, index=False, sep=";")
logger.info(f"[INFO] CSV de teste criado: {csv_test_file}")

# XLSX de teste
df_xlsx = df_csv.copy()
df_xlsx.to_excel(xlsx_test_file, index=False)
logger.info(f"[INFO] Excel de teste criado: {xlsx_test_file}")

# --- Executar transformação ---
transformer = CSVTransformer(input_dir=processed_dir, output_dir=transformed_dir)

# Listar todos os arquivos da pasta processed
files_to_transform = [f for f in os.listdir(processed_dir) 
                      if os.path.isfile(os.path.join(processed_dir, f)) 
                      and f.lower().endswith(('.csv', '.xls', '.xlsx'))]

for file in files_to_transform:
    try:
        df_transformed = transformer.transform_file(file)
        logger.info(f"[SUCESSO] Transformação concluída: {file}")
        logger.info(f"[DATAFRAME RESULTANTE]\n{df_transformed}")

        # Verificar se o arquivo foi movido
        dest_path = os.path.join(transformed_dir, file)
        if os.path.exists(dest_path):
            logger.info(f"[OK] Arquivo transformado está na pasta transformed: {dest_path}")
        else:
            logger.error(f"[ERRO] Arquivo não encontrado na pasta transformed: {dest_path}")

    except Exception as e:
        logger.error(f"[ERRO] Falha ao executar o teste: {e}")

logger.info("[INFO] Teste de transformação concluído.")
