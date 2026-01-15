import re
from typing import Optional

def extract_text(raw_content: Optional[str]) -> str:
    """
    Extrai texto puro de um conteúdo bruto, removendo marcações estruturais comuns como HTML.

    Args:
        raw_content: A string de entrada, que pode conter marcações estruturais ou ser None.

    Returns:
        Uma string contendo apenas texto puro. Retorna uma string vazia se a entrada for None
        ou não puder ser processada.
    """
    if not isinstance(raw_content, str):
        return ""

    # Remove elementos <script> e <style>
    # As flags (?is) ativam a correspondência sem distinção entre maiúsculas e minúsculas e fazem com que '.' corresponda a novas linhas.
    clean_text = re.sub(r'(?is)<(script|style).*?>.*?</\1>', '', raw_content)
    
    # Remove as tags HTML restantes
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    
    # Decodifica entidades HTML
    import html
    clean_text = html.unescape(clean_text)
    
    # Preserva quebras de linha relevantes ao não tocá-las após a remoção das tags.
    return clean_text.strip()
