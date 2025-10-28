import re
import unicodedata

class TextFormatter:
    "classe para padronizar os textos"

    def __init__(self, case="title", remove_accents=True, clean_spaces=True):
        self.case = case
        self.remove_accents = remove_accents
        self.clean_spaces = clean_spaces
    
    def format(self, text:str) -> str:
        
        if not isinstance(text, str):
            return text
        
        if self.clean_spaces:
            text = re.sub(r'\s+', ' ', text.strip())

        if self.remove_accents:
            text = ''.join(
                c for c in unicodedata.normalize('NFD', text)
                if unicodedata.category(c) != 'Mn'
            )

        if self.case == 'upper':
            text = text.upper()
        elif self.case == 'lower':
            text = text.lower()
        elif self.case == 'title':
            text = text.title()

        return text