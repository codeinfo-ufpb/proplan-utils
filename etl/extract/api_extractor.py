import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from core.base_extractor import BaseExtractor
from extract.extraction_models import ExtractionResult, SourceMetadata
from common.logging_utils import get_logger


class APIExtractor(BaseExtractor):
    """ Classe responsável por se comunicar com APIS REST, pagina e normalizar JSON em DataFrames."""

    def __init__(self, name: str, api_endpoint: str, headers: Dict[str, str]):
        self.logger = get_logger(f"api-extractor-{name}")
        self.name = name
        self.api_endpoint = api_endpoint
        self.headers = headers
    
    def extract(self, *args, **kwargs) -> List[ExtractionResult]:
        self.logger.info(f"Iniciando a extração da API para a fonte: {self.name} ({self.api_endpoint})")
        
        # OBSERVAÇÃO: Em um cenário real utilizaremos HTTPS:
        # response = requests.get(self.api_endpoint, headers=self.headers)
        # data = response.json()

        try:
            data = [
                {'metric_name': 'usage_count', 'value': 1500, 'timestamp': datetime.now()},
                {'metric_name': 'latency_ms', 'value': 250, 'timestamp': datetime.now()}
            ]

            df = pd.DataFrame(data)

            source_meta = SourceMetadata(
                message_id=f"api-{self.name}-{datetime.now().timestamp()}",
                sender_email="system@api.external",
                subject=f"API Call Result: {self.name}",
                date_received=datetime.now(),
                other_info={"source_type": "API", "endpoint": self.api_endpoint}
            )

            self.logger.info(f"Extração API concluída. {len(df)} registros lidos.")
            

            return [ExtractionResult(original_filename=f"{self.name}_metrics.json", dataframe=df, source=source_meta)]

        except Exception as e:
            self.logger.error(f"Falha na extração da API para {self.name}. Erro: {e}")
            return []