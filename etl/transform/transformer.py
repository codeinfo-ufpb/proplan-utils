import os
import pandas as pd
import re
import numpy as np
import unicodedata
from pathlib import Path
from config.settings import settings
from common.logging_utils import get_logger
from core.base_transformer import BaseTransformer
from shutil import move
from .domain_rules import normalizar_auxilios_pi, classificar_grupo_auxilio

class CSVTransformer(BaseTransformer):
    """Classe responsável por aplicar as transformações e padronizações em arquivos CSV ou XLSX já processados pela etapa de extração. Os arquivos devem estar localizados em data/processed."""

    def __init__(self, input_dir: None, output_dir: None):
        super().__init__()
        self.input_dir = Path(settings.DIR_PROCESSED)
        self.output_dir = Path(settings.DIR_TRANSFORMED)
        self.logger = get_logger("csv-transformer")

    def harmonize_column_headers(self, df=None):
        """
        Método para harmonizar os cabeçalhos duplicados e substitui 'Unnamed' pelos nomes válidos da última coluna conhecida.
        Exemplo: 'Unnamed: 4' -> 'Resultado Primário Lei: 4'
        """
        if df is None:
            df = self.dataframe.copy()
        else:
            df = df.copy()

        new_columns = []
        last_valid = None

        for col in df.columns:
            col_str = str(col).strip()

            # Se for uma coluna "unnamed", herdamos o nome anterior
            if col_str.lower().startswith("unnamed"):
                if last_valid:
                    # Pegamos o número da coluna Unnamed (ex: 'Unnamed: 13')
                    num = ''.join(filter(str.isdigit, col_str))
                    col_str = f"{last_valid}: {num}" if num else last_valid
                else:
                    col_str = "Coluna_Sem_Titulo"
            else:
                last_valid = col_str

            new_columns.append(col_str)

        df.columns = new_columns
        self.logger.info("[OK] Cabeçalhos harmonizados com sucesso.")
        return df

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
            """
            Método para normalizar os nomes das colunas e remover colunas 'Unnamed' sem causar incompatibilidade.
            """
            df_copy = df.copy()
            # Cria o mapa de renomeação (apenas para colunas que NÃO são 'Unnamed')
            renaming_map = {}
            columns_to_drop = []
            
            for col in df_copy.columns:
                col_str = str(col).strip()
                normalized_col = col_str.lower().replace(" ", "_").replace(".", "_").replace("-", "_").replace("/", "___")
                
                if normalized_col.startswith("unnamed:"):
                    # Marca para exclusão
                    columns_to_drop.append(col)
                    self.logger.warning(f"[AVISO] Coluna 'Unnamed' marcada para exclusão: {col}")
                else:
                    # Mapeia para renomeação
                    renaming_map[col] = normalized_col
                    
            # Renomeia as colunas válidas (que não foram marcadas para exclusão)
            df_copy = df_copy.rename(columns=renaming_map)
            
            # Remove as colunas 'Unnamed' que sobraram
            if columns_to_drop:
                # errors='ignore' garante que não falhe se a coluna já tiver sido removida por algum motivo
                df_copy = df_copy.drop(columns=columns_to_drop, errors='ignore') 
            
            self.logger.info(f"[OK] Colunas normalizadas e 'Unnamed' removidas. Total de colunas: {len(df_copy.columns)}")
            
            return df_copy

    def handle_merged_cells(self, df: pd.DataFrame) -> pd.DataFrame:
            """
            Trata valores NaN resultantes de células mescladas, aplicando ffill() 
            apenas em colunas chave que DEVEM conter o valor da linha superior.
            """
            df_copy = df.copy()

            # Defina as colunas que você sabe que são chaves mestras e foram mescladas
            # Se os nomes de coluna estiverem normalizados no pipeline:
            KEY_COLS_TO_FFILL = [
                'ano_lancamento', 
                'ob___lista_credores', 
                'mes_lancamento', 
                # Colunas de descrição ou PI (se não forem usadas para cálculos)
                'ob/lc___favorecido', 
                # ... adicione outras colunas de identificação aqui.
            ]
            
            # Filtra apenas as colunas que existem no DataFrame
            cols_to_fill = [col for col in KEY_COLS_TO_FFILL if col in df_copy.columns]
            
            if cols_to_fill:
                # Aplica ffill() SOMENTE nas colunas identificadas
                df_copy[cols_to_fill] = df_copy[cols_to_fill].ffill()
                self.logger.info(f"[OK] Aplicado ffill() para células mescladas nas chaves: {cols_to_fill}")
            else:
                self.logger.info("[INFO] Nenhuma coluna chave para ffill() identificada.")
                
            return df_copy
    
    def load_file(self, filename: str) -> pd.DataFrame:
        file_path = os.path.join(self.input_dir, filename)

        if not os.path.exists(file_path):
            self.logger.error(f"Arquivo não encontrado: {file_path}")
            raise FileNotFoundError(file_path)

        self.logger.info(f"[STATUS] Carregando arquivo..: {file_path}")

        if filename.lower().endswith(('.xls', '.xlsx')):
            # Detectar automaticamente onde está o cabeçalho
            preview = pd.read_excel(file_path, header=None, nrows=10)
            header_row = None
            for i, row in preview.iterrows():
                if any(str(cell).strip().lower().startswith("ano") for cell in row):
                    header_row = i
                    break

            if header_row is None:
                header_row = 2  # fallback padrão
                self.logger.warning("[AVISO] Cabeçalho não encontrado automaticamente, usando linha 3.")

            df = pd.read_excel(file_path, header=header_row)
        else:
            df = pd.read_csv(file_path, sep=";", encoding="utf-8", engine="python")

        # 🚿 Remover colunas Unnamed
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        # 🧹 Limpar nomes das colunas
        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

        self.logger.info(f"[OK] Arquivo carregado e normalizado. Dimensões: {df.shape}")
        return df

    def transform_text_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove espaços extras, normaliza texto e padroniza o conteúdo das colunas de texto.
        A padronização dos NOMES das colunas é feita em _harmonize_and_normalize_columns.
        """
        
        def clean_string(text):
            if isinstance(text, str):
                # Normaliza para o caractere base do texto (remove acentos)
                normalized_text = unicodedata.normalize('NFKD', text).encode("ascii","ignore").decode("ascii") 
                text_upper = normalized_text.upper() # Transformar tudo em maiúsculas
                text_stripped = text_upper.strip() # Remover os espaços no início e no fim
                # Substituir múltiplos espaços, caracteres não alfanuméricos por um único espaço
                text_spaced = re.sub(r"[^\w\s/.-]", " ", text_stripped) 
                return re.sub(r'\s+', ' ', text_spaced).strip()
            return text
            
        # Aplica a função de limpeza SOMENTE nas colunas de texto (object)
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(clean_string)
            
        self.logger.info("[OK] Limpeza e padronização de conteúdo de texto concluída.")
        return df
    
    def apply_domain_specific_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """ 
        Aplica as transformações específicas para os domínio de Auxílios PI etc. 
         - Neste caso, apenas se as colunas de referência ('ds_pi' e 'ds_ug') existirem. (ajustável)
        """
        # Verifica a existência das colunas para saber se é um arquivo de Domínio PI
        if 'ds_pi' in df.columns and 'ds_ug' in df.columns:
            self.logger.info("-> Aplicando Feature e Classificação de Domínio (Auxílios PI)...")
            
            try:           
                # Normalização Detalhada (tipo, campus, nível)
                df = normalizar_auxilios_pi(df) 
                # Classificação Macro (grupo_auxilio, origem_classif)
                df = classificar_grupo_auxilio(df)
                
                self.logger.info("[OK] Regras de Domínio Auxílios PI aplicadas: tipo_auxilio, grupo_auxilio, etc.")
                
            except Exception as e:
                self.logger.error(f"[ERRO] Falha crítica ao aplicar regras de domínio PI: {e}")
                
        else:
            self.logger.info("-> Colunas de Domínio PI não encontradas. Pulando Regras Específicas.")
            
        return df

    def convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converte os tipos de colunas automaticamente quando aplicável.
        """
        # Converter colunas de data
        
        KEYWORDS_DATA = ["data", "date", "dt", "nasc", "nascimento", "admissao", "vencimento", "venc", "admis", "vigencia", "cria", "cadastro", "inclusao", "fim", "inicio", "update", "ts", "hr", "time"]
        keyword_pattern = r'\b(' + '|'.join(KEYWORDS_DATA) + r')\b'
        DATE_PATTERN = keyword_pattern + r"|_at$|_date$|_ts$|^(dt|data|hr)_"

        for col in df.columns:
            if re.search(DATE_PATTERN, col.lower()):
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
                except Exception:
                    pass

        # converter colunas numéricas
        NUMERIC_THRESHOLD = 0.80
        for col in df.select_dtypes(include=['object']).columns:
            cleaned_col = (df[col].astype(str).str.replace("%", "", regex=False).str.strip().str.replace(r'\.', '', regex=True).str.replace(",", ".", regex=False)) # Trata %, espaços extras, remove ponto de milhar e troca vírgula por ponto de milhar.
            converted_col = pd.to_numeric(cleaned_col, errors="coerce") #Converterá valores inválidos para NaN
            if converted_col.notna().sum()/len(converted_col) >=  NUMERIC_THRESHOLD:
                df[col] = converted_col
        df = df.convert_dtypes()
        for col in df.select_dtypes(include=['Int64']).columns: 
            # Se a coluna já for Int64, segue o fluxo.
            if df[col].dtype.kind == 'f':  # Se o tipo ainda for float (f)
                if (df[col].dropna() % 1 == 0).all(): 
                    df[col] = df[col].astype('Int64', errors='ignore')

        self.logger.info("[OK] Conversão de tipos concluída, utilizando tipos nulos (Int64) para robustez.")
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
            """
            Trata valores ausentes (NaN) no DataFrame com base no tipo de coluna:
            - Numéricas: Preenchidas com a MEDIANA (mais robusta a outliers).
            - Categóricas/Texto: Preenchidas com a MODA (valor mais frequente).
            - Se a moda for NaN (ex: coluna com 100% NaN), usa 'Ausente'.
            """
            
            # Cria uma cópia para evitar SettingWithCopyWarning
            df_cleaned = df.copy() 
            
            print("--- Iniciando Tratamento de Valores Ausentes (NaN) ---")

            # 1. Tratamento para Colunas Numéricas (int, float, etc.)
            numeric_cols = df_cleaned.select_dtypes(include=['number']).columns
            
            for col in numeric_cols:
                # A mediana é geralmente mais segura do que a média, pois não é distorcida por outliers.
                median_value = df_cleaned[col].median()
                
                # Aplica a imputação
                if pd.notna(median_value):
                    df_cleaned[col].fillna(median_value, inplace=True)
                    print(f"-> Coluna '{col}' (Numérica): Preenchida com a Mediana ({median_value:.2f}).")
                else:
                    # Caso a mediana seja NaN (ex: coluna 100% vazia), preenche com 0 (ou outro valor seguro)
                    df_cleaned[col].fillna(0, inplace=True)
                    print(f"-> Coluna '{col}' (Numérica): Mediana não disponível. Preenchida com 0.")


            # 2. Tratamento para Colunas Categóricas/Texto (object, category, etc.)
            categorical_cols = df_cleaned.select_dtypes(include=['object', 'category']).columns

            for col in categorical_cols:
                # A moda (valor mais frequente) é a melhor escolha para dados categóricos.
                mode_value = df_cleaned[col].mode()
                
                if not mode_value.empty:
                    # O .mode() retorna uma Series; [0] pega o primeiro (o mais frequente)
                    impute_value = mode_value[0]
                    df_cleaned[col].fillna(impute_value, inplace=True)
                    print(f"-> Coluna '{col}' (Categórica): Preenchida com a Moda ('{impute_value}').")
                else:
                    # Fallback: Se não houver moda (ex: todos os valores são NaN ou únicos), 
                    # preenche com uma etiqueta informativa.
                    df_cleaned[col].fillna("Ausente", inplace=True)
                    print(f"-> Coluna '{col}' (Categórica): Moda não disponível. Preenchida com 'Ausente'.")

            print("--- Tratamento de Valores Ausentes Concluído ---")
            return df_cleaned

    def handle_outliers(self, df: pd.DataFrame, factor: float = 1.5) -> pd.DataFrame:
            """
            Identifica e trata outliers em colunas numéricas usando o método do 
            Intervalo Interquartil (IQR) com 'Clamping' (Winsorizing).

            Os outliers são substituídos pelo limite superior ou inferior do IQR.
            
            Args:
                df (pd.DataFrame): O DataFrame a ser processado.
                factor (float): O fator multiplicador para o IQR (padrão é 1.5).
                
            Returns:
                pd.DataFrame: O DataFrame com os outliers tratados.
            """
            
            df_cleaned = df.copy() 
            
            print("--- Iniciando Tratamento de Outliers (Método IQR) ---")

            # Seleciona apenas colunas numéricas (incluindo float e int)
            numeric_cols = df_cleaned.select_dtypes(include=np.number).columns
            
            for col in numeric_cols:
                
                # Pula colunas que não são apropriadas para detecção de outliers (ex: colunas binárias)
                if df_cleaned[col].nunique() <= 5: 
                    continue
                    
                # 1. Calcula o IQR (Intervalo Interquartil)
                Q1 = df_cleaned[col].quantile(0.25)
                Q3 = df_cleaned[col].quantile(0.75)
                IQR = Q3 - Q1
                
                # 2. Define os Limites (usando o fator 1.5, que é o padrão de Tukey)
                lower_bound = Q1 - factor * IQR
                upper_bound = Q3 + factor * IQR
                
                # 3. Identifica o número de outliers
                outliers_count = (
                    (df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)
                ).sum()
                
                if outliers_count > 0:
                    # 4. Tratamento por Clamping (Winsorizing):
                    # Substitui valores abaixo do limite inferior pelo próprio limite inferior
                    df_cleaned[col] = np.where(
                        df_cleaned[col] < lower_bound,
                        lower_bound,
                        df_cleaned[col]
                    )
                    
                    # Substitui valores acima do limite superior pelo próprio limite superior
                    df_cleaned[col] = np.where(
                        df_cleaned[col] > upper_bound,
                        upper_bound,
                        df_cleaned[col]
                    )
                    
                    print(f"-> Coluna '{col}': {outliers_count} outliers tratados por Clamping (Limites: {lower_bound:.2f} e {upper_bound:.2f}).")
            
            print("--- Tratamento de Outliers Concluído ---")
            return df_cleaned

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
                """
                Cria novas variáveis (features) a partir de colunas de Data/Hora.
                Utiliza 'Int64' (Nullable Integer) para garantir que valores NaT/NaN 
                não causem falha de conversão para int.
                """
                self.logger.info("--- Iniciando Criação de Variáveis (Feature Engineering) ---") # Usando logger
                
                df_cleaned = df.copy() 
                
                datetime_cols = df_cleaned.select_dtypes(include=['datetime64']).columns
                
                if datetime_cols.empty:
                    self.logger.info("Nenhuma coluna do tipo datetime64 encontrada para Feature Engineering.")
                    return df_cleaned

                # Define o tipo Nullable Integer para todas as novas features inteiras
                INT_NULLABLE = 'Int64' 

                for col in datetime_cols:
                    base_name = col
                    
                    if df_cleaned[col].notna().any():
                        
                        # Extração Comum: Dia, Mês e Ano - CORRIGIDO com INT_NULLABLE
                        df_cleaned[f'{base_name}_ano'] = df_cleaned[col].dt.year.astype(INT_NULLABLE)
                        df_cleaned[f'{base_name}_mes'] = df_cleaned[col].dt.month.astype(INT_NULLABLE)
                        df_cleaned[f'{base_name}_dia'] = df_cleaned[col].dt.day.astype(INT_NULLABLE)
                        
                        # Correção: O dayofweek também deve ser Nullable
                        df_cleaned[f'{base_name}_dia_semana'] = df_cleaned[col].dt.dayofweek.astype(INT_NULLABLE)
                        
                        # Extração de Tempo
                        if df_cleaned[col].dt.hour.max() > 0:
                            df_cleaned[f'{base_name}_hora'] = df_cleaned[col].dt.hour.astype(INT_NULLABLE)
                        
                        # Extração de Sazonalidade - CORRIGIDO com INT_NULLABLE
                        df_cleaned[f'{base_name}_trimestre'] = df_cleaned[col].dt.quarter.astype(INT_NULLABLE)
                        
                        # CORREÇÃO CRÍTICA: isocalendar().week já retorna um tipo compatível com Int64 no Pandas >= 1.1,
                        # mas o astype(INT_NULLABLE) garante a compatibilidade com a versão.
                        # Nota: isocalendar pode retornar uma série com tipo Period, então a conversão direta é mais segura.
                        df_cleaned[f'{base_name}_semana_ano'] = df_cleaned[col].dt.isocalendar().week.astype(INT_NULLABLE)


                        self.logger.info(f"-> Features criadas a partir de '{col}' usando {INT_NULLABLE}.")
                    
                self.logger.info("--- Criação de Variáveis Concluída ---")
                return df_cleaned
    
    def encode_categorical_features(self, df: pd.DataFrame, max_onehot_categories: int = 15) -> pd.DataFrame:
        """
        Codifica colunas categóricas (object/category) para o formato numérico.

        Aplica One-Hot Encoding para colunas com até 'max_onehot_categories'
        e Label Encoding para colunas com muitas categorias (High Cardinality).

        Args:
            df (pd.DataFrame): O DataFrame a ser processado.
            max_onehot_categories (int): Limite de categorias para aplicar One-Hot Encoding.
                                         Variáveis com mais categorias usam Label Encoding.
                                         
        Returns:
            pd.DataFrame: O DataFrame com as features categóricas codificadas.
        """
        
        df_encoded = df.copy() 
        
        print("--- Iniciando Codificação de Variáveis Categóricas ---")

        # 1. Identifica colunas categóricas (texto)
        categorical_cols = df_encoded.select_dtypes(include=['object', 'category']).columns
        
        if categorical_cols.empty:
            print("Nenhuma coluna categórica encontrada para codificação.")
            return df_encoded

        one_hot_cols = []
        label_cols = []

        for col in categorical_cols:
            n_unique = df_encoded[col].nunique()
            
            # Se for uma coluna binária (True/False, Sim/Não, M/F), o Label Encoding 
            # é suficiente e mais eficiente que o One-Hot.
            if n_unique <= 2:
                label_cols.append(col)
                
            # One-Hot para variáveis nominais com poucas categorias
            elif n_unique <= max_onehot_categories:
                one_hot_cols.append(col)
            
            # Label Encoding para variáveis com alta cardinalidade (> max_onehot_categories)
            else:
                label_cols.append(col)
        
        # --- 2. Aplica ONE-HOT ENCODING (para colunas nominais com baixa cardinalidade) ---
        if one_hot_cols:
            # pd.get_dummies é o método mais eficiente e seguro
            # drop_first=True evita multicolinearidade (útil para modelos de regressão)
            df_encoded = pd.get_dummies(
                df_encoded, 
                columns=one_hot_cols, 
                prefix=one_hot_cols, 
                drop_first=True,
                dtype=int
            )
            print(f"-> One-Hot Encoding aplicado a: {', '.join(one_hot_cols)}.")


        # --- 3. Aplica LABEL ENCODING (para colunas ordinais ou de alta cardinalidade) ---
        if label_cols:
            for col in label_cols:
                # O .astype('category').cat.codes mapeia automaticamente as strings para inteiros (0, 1, 2, ...)
                df_encoded[col] = df_encoded[col].astype('category').cat.codes
            
            print(f"-> Label Encoding aplicado a: {', '.join(label_cols)}.")

        print("--- Codificação Categórica Concluída ---")
        return df_encoded
    
    def map_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica mapeamentos personalizados em colunas específicas. Neste exemplo estamos tratando sobre licitações.
        """
        mapping = {
            'CD': 'Compra Direta',
            'PE': 'Pregão Eletrônico',
            'CV': 'Convite',
            'PP': 'Pregão Presencial',
            'IN': 'Inexigibilidade',
            'CC': 'Concorrência',
        }

        if 'tipo' in df.columns:
            df['tipo'] = df['tipo'].replace(mapping)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executará todas as transformações.
        """
        self.logger.info("[INFO] Iniciando transformações básicas...")
        df = self.transform_text_columns(df)
        df = self.convert_types(df)
        df = self.map_values(df)
        df.dropna(how="all", inplace=True)
        self.logger.info(f"[OK] Transformações aplicadas. Shape final: {df.shape}")
        return df

    def transform_file(self, filename: str) -> pd.DataFrame:
        """
        Executa o processo completo de transformação e move o arquivo para transformed.
        """
        df = self.load_file(filename)
        df_transformed = self.execute(df)

        # Cria a pasta caso não exista. Garantirá que a pasta de saída existe
        os.makedirs(self.output_dir, exist_ok=True)

        src_path = os.path.join(self.input_dir, filename)
        dest_path = os.path.join(self.output_dir, filename)

        try:
            move(src_path, dest_path)
            self.logger.info(f"[OK] Arquivo original movido para: {dest_path}")
        except Exception as e:
            self.logger.error(f"Ops! [ERRO] Falha ao mover arquivo: {e}")

        return df_transformed

# ----------------------------------------------------------------------
    # 3. MÉTODO CENTRAL DE EXECUÇÃO (PIPELINE)
    # ----------------------------------------------------------------------
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executa todas as transformações na ordem lógica do pipeline.
        """
        self.logger.info("[INFO] Iniciando o pipeline completo de transformações...")

        # 0. Início da normalização das colunas
        df = self.harmonize_column_headers(df)
        
        # 1. Limpeza de Texto (Strings) - Agora unificada e robusta
        df = self.transform_text_columns(df)

        df = self.handle_merged_cells(df)
        
        # 2. Conversão de Tipos (Datas e Numéricos) - (Assumindo que este método existe)
        df = self.convert_types(df)
        
        # 3. APLICAÇÃO DE REGRAS DE DOMÍNIO ESPECÍFICO (Modular)
        df = self.apply_domain_specific_rules(df) 
        
        # 4. Tratamento de Valores Ausentes (NaNs) - (Trata NaNs criados/deixados pelas etapas 2 e 3)
        df = self.handle_missing_values(df)
        
        # 5. Tratamento de Outliers (Clamping)
        df = self.handle_outliers(df)
        
        # 6. Feature Engineering (Datas)
        df = self.create_features(df)
        
        # 7. Mapeamento Personalizado
        df = self.map_values(df) 
        
        # 8. Codificação Categórica
        df = self.encode_categorical_features(df)
        
        # 9. Limpeza Final
        df.dropna(how="all", inplace=True)
        
        self.logger.info(f"[OK] Pipeline de transformações concluído. Shape final: {df.shape}")
        return df
