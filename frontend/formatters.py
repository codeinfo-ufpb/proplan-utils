import unicodedata
from datetime import datetime


def format_currency(value, symbol="R$", decimals=2):
    """
    Formata o número no formato comum para o formato de moeda brasileira (Real).
    Por Exemplo: format_currency(10.5) -> 'R$ 10,50'
    """
    if value is None:
        return "-"
    return f"{symbol} {value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_percent(value, decimals=2):
    """
    Formata número como percentual.
    Exemplo: format_percent(0.1234) -> '12,34%'
    """
    if value is None:
        return "-"
    return f"{value * 100:.{decimals}f}%".replace(".", ",")

def format_date(date_value, fmt="%d/%m/%Y"):
    """
    Formata data para string.
    Aceita datetime, string ISO ou timestamp.
    """
    if not date_value:
        return "-"
    if isinstance(date_value, (int, float)):
        date_value = datetime.fromtimestamp(date_value)
    elif isinstance(date_value, str):
        try:
            date_value = datetime.fromisoformat(date_value)
        except ValueError:
            return date_value
    return date_value.strftime(fmt)

def normalize_text(text, to_lower=True):
    """
    Método que remove acentos e espaços extras, converte maiúsculas/minúsculas.
    """
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    text = text.strip()
    return text.lower() if to_lower else text.upper()

