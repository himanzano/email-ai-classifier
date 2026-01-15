import re
import os
from typing import Optional

def extract_text(raw_content: Optional[str]) -> str:
    """
    Extrai texto puro de um conteúdo bruto, removendo marcações estruturais comuns como HTML.
    Pode processar strings diretas, HTML, ou um caminho para um arquivo .txt.

    Args:
        raw_content: A string de entrada, que pode ser texto, HTML, um caminho de arquivo .txt, ou None.

    Returns:
        Uma string contendo apenas texto puro. Retorna uma string vazia se a entrada for None,
        inválida, ou se o arquivo não puder ser lido.
    """
    if not isinstance(raw_content, str) or not raw_content.strip():
        return ""

    content_to_process = raw_content
    potential_path = raw_content.strip()

    # Se a entrada parece ser um caminho para um arquivo .txt, tente lê-lo.
    if potential_path.endswith('.txt'):
        if os.path.isfile(potential_path):
            try:
                with open(potential_path, 'r', encoding='utf-8') as f:
                    content_to_process = f.read()
            except (IOError, UnicodeDecodeError):
                # O arquivo existe, mas não pode ser lido/decodificado.
                return ""
        else:
            # O caminho termina em .txt, mas não é um arquivo válido.
            return ""

    # Remove elementos <script> e <style> do conteúdo.
    # As flags (?is) ativam a correspondência sem distinção entre maiúsculas e minúsculas e fazem com que '.' corresponda a novas linhas.
    clean_text = re.sub(r'(?is)<(script|style).*?>.*?</\1>', '', content_to_process)

    # Remove as tags HTML restantes.
    clean_text = re.sub(r'<[^>]+>', '', clean_text)

    # Decodifica entidades HTML (ex: &amp; para &).
    import html
    clean_text = html.unescape(clean_text)

    # Retorna o texto limpo, removendo espaços em branco no início/fim.
    return clean_text.strip()