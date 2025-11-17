from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
import pandas as pd

@dataclass
class SourceMetadata:
    """Metadados da fonte original (E-mail)."""
    # Identificador da mensagem (e.g., Message-ID ou UID)
    message_id: str
    # Endereço do remetente (Que enviou o e-mail)
    sender_email: str
    # Assunto do e-mail
    subject: str
    # Data de recebimento do e-mail
    date_received: datetime
    # Outros campos úteis
    other_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExtractionResult:
    """Resultado final da extração de um único arquivo."""
    # Nome original do arquivo
    original_filename: str
    # DataFrame normalizado e validado
    dataframe: pd.DataFrame
    # Metadados do e-mail de onde o arquivo foi extraído
    source: SourceMetadata
    # Carimbo de data/hora de quando o processo de extração terminou
    extract_timestamp: datetime = field(default_factory=datetime.now)

# O run() do ExtractManager retornará uma lista deste tipo:
# List[ExtractionResult]