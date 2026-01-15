import re
import os
from typing import Optional
from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdfminer.pdfparser import PDFSyntaxError


def _extract_text_from_pdf(file_path: str) -> str:
    """
    Extrai texto puro de um arquivo PDF de forma segura, usando pdfminer.six.
    Retorna uma string vazia se ocorrer um erro.
    """
    try:
        # A função de alto nível do pdfminer.six lida com a abertura e extração.
        text = pdfminer_extract_text(file_path)
        return text if text else ""
    except (PDFSyntaxError, Exception):
        # Captura erros específicos da biblioteca ou qualquer outra exceção inesperada.
        return ""


def extract_text(raw_content: Optional[str]) -> str:
    """
    Extrai texto puro de um conteúdo bruto. Pode processar strings diretas, HTML,
    ou caminhos para arquivos .txt e .pdf.

    Args:
        raw_content: A string de entrada (texto, HTML, caminho de arquivo) ou None.

    Returns:
        Uma string contendo apenas texto puro. Retorna string vazia se a entrada for
        inválida ou se o arquivo não puder ser lido.
    """
    if not isinstance(raw_content, str) or not raw_content.strip():
        return ""

    content_to_process = raw_content
    potential_path = raw_content.strip()

    # Decide o tipo de conteúdo e o processa.
    if potential_path.endswith('.txt'):
        if os.path.isfile(potential_path):
            try:
                with open(potential_path, 'r', encoding='utf-8') as f:
                    content_to_process = f.read()
            except (IOError, UnicodeDecodeError):
                return ""
        else:
            return ""
    elif potential_path.endswith('.pdf'):
        if os.path.isfile(potential_path):
            content_to_process = _extract_text_from_pdf(potential_path)
            # Se a extração do PDF falhar, retorna string vazia imediatamente.
            if not content_to_process:
                return ""
        else:
            return ""

    # O conteúdo (de string, .txt ou .pdf) passa pelo pipeline de limpeza de HTML.
    # 1. Remove elementos <script> e <style>.
    clean_text = re.sub(r'(?is)<(script|style).*?>.*?</\1>', '', content_to_process)

    # 2. Remove as tags HTML restantes.
    clean_text = re.sub(r'<[^>]+>', '', clean_text)

    # 3. Decodifica entidades HTML.
    import html
    clean_text = html.unescape(clean_text)

    # Retorna o texto limpo, removendo espaços em branco no início/fim.
    return clean_text.strip()
