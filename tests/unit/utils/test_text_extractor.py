from app.utils.text_extractor import extract_text
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


# --- Testes Existentes ---


def test_none_input_returns_empty_string():
    """Testa se a entrada None retorna uma string vazia."""
    assert extract_text(None) == ""


def test_empty_string_returns_empty_string():
    """Testa se uma string vazia de entrada retorna uma string vazia."""
    assert extract_text("") == ""


def test_plain_text_returns_unchanged():
    """Testa se texto puro sem marcação é retornado inalterado."""
    plain_text = "Esta é uma string de texto puro."
    assert extract_text(plain_text) == plain_text


def test_text_with_basic_html_tags_removed():
    """Testa se as tags HTML básicas são removidas do texto."""
    html_text = "<h1>Título</h1><p>Este é um <b>conteúdo</b> com <i>formatação</i>.</p>"
    expected_text = "TítuloEste é um conteúdo com formatação."
    assert extract_text(html_text) == expected_text


def test_line_breaks_preserved():
    """Testa se quebras de linha relevantes são preservadas."""
    text_with_breaks = "Linha 1\nLinha 2\n\nLinha 4."
    assert extract_text(text_with_breaks) == text_with_breaks


def test_html_with_line_breaks_and_entities():
    """Testa uma mistura de HTML, quebras de linha e entidades HTML."""
    mixed_content = (
        "<div>Olá &amp; Mundo!<br>"
        "<span>Esta é uma nova linha.</span></div>\n"
        "<p>Outro parágrafo &copy; 2023.</p>"
    )
    expected_output = "Olá & Mundo!Esta é uma nova linha.\nOutro parágrafo © 2023."
    assert extract_text(mixed_content) == expected_output


def test_text_with_extra_spaces_and_tabs():
    """Testa se espaços extras e tabulações são tratados e se o espaço em branco inicial/final é removido."""
    text = "  Olá   Mundo\t!  \n"
    expected_text = "  Olá   Mundo\t!  \n"
    assert extract_text(text) == expected_text.strip()


def test_unexpected_input_types_return_empty_string():
    """Testa se tipos de entrada inesperados (não-str, não-None) retornam uma string vazia sem exceções."""
    assert extract_text(123) == ""  # type: ignore
    assert extract_text(["lista", "de", "strings"]) == ""  # type: ignore
    assert extract_text({"chave": "valor"}) == ""  # type: ignore
    assert extract_text(True) == ""  # type: ignore


def test_complex_html_entities_decoded():
    """Testa a decodificação de entidades HTML mais complexas."""
    html_entity_text = "&quot;Olá&quot; &ndash; Mundo &#x2014; Teste"
    expected_text = '"Olá" – Mundo — Teste'
    assert extract_text(html_entity_text) == expected_text


def test_script_tags_removed():
    """Testa se as tags de script e seu conteúdo são removidos."""
    script_html = "<div><script>alert('Olá');</script>Texto normal.</div>"
    expected_text = "Texto normal."
    assert extract_text(script_html) == expected_text


def test_style_tags_removed():
    """Testa se as tags de estilo e seu conteúdo são removidos."""
    style_html = "<div><style>body { color: red; }</style>Texto normal.</div>"
    expected_text = "Texto normal."
    assert extract_text(style_html) == expected_text


def test_malformed_html_no_exception():
    """Testa se HTML malformado não causa uma exceção e é tratado graciosamente."""
    malformed_html = "<div><p>Tag não fechada<div>Texto normal."
    expected_text = "Tag não fechadaTexto normal."
    assert extract_text(malformed_html) == expected_text


# --- Testes para .txt ---


def test_extract_text_from_valid_txt_file(tmp_path):
    """Testa a extração de texto a partir de um arquivo .txt válido."""
    p = tmp_path / "arquivo_valido.txt"
    conteudo = "Olá, mundo!"
    p.write_text(conteudo, encoding="utf-8")
    assert extract_text(str(p)) == conteudo


def test_extract_text_from_empty_txt_file(tmp_path):
    """Testa se um arquivo .txt vazio retorna uma string vazia."""
    p = tmp_path / "arquivo_vazio.txt"
    p.touch()
    assert extract_text(str(p)) == ""


def test_non_existent_txt_file_path_returns_empty_string(tmp_path):
    """Testa se o caminho para um arquivo .txt inexistente retorna uma string vazia."""
    p = tmp_path / "arquivo_inexistente.txt"
    assert extract_text(str(p)) == ""


def test_txt_file_with_html_content_is_cleaned(tmp_path):
    """Testa se um arquivo .txt contendo HTML tem as tags removidas."""
    p = tmp_path / "arquivo_com_html.txt"
    conteudo_html = "<h1>Título</h1><p>Texto com <b>negrito</b>.</p>"
    conteudo_esperado = "TítuloTexto com negrito."
    p.write_text(conteudo_html, encoding="utf-8")
    assert extract_text(str(p)) == conteudo_esperado


def test_path_not_ending_in_txt_is_treated_as_string(tmp_path):
    """Testa se uma entrada que aponta para um arquivo que não é .txt é tratada como string."""
    p = tmp_path / "nao_e_um_txt.log"
    p.write_text("Conteúdo que não deve ser lido.", encoding="utf-8")
    # A função não deve ler o arquivo, mas sim tratar o caminho como texto puro.
    # O HTML extractor não fará nada, então o resultado deve ser o próprio caminho.
    assert extract_text(str(p)) == str(p)


# --- Novos Testes para .pdf ---


def _create_pdf(path, text_content=None):
    """Gera um PDF simples para testes."""
    c = canvas.Canvas(str(path), pagesize=letter)
    if text_content:
        text_object = c.beginText()
        text_object.setTextOrigin(72, 800)  # Posição do texto
        text_object.setFont("Helvetica", 10)
        text_object.textLines(text_content)
        c.drawText(text_object)
    c.save()


def test_extract_text_from_valid_pdf_file(tmp_path):
    """Testa a extração de texto a partir de um arquivo PDF válido."""
    pdf_path = tmp_path / "valid.pdf"
    content = "Este é o conteúdo de um arquivo PDF."
    _create_pdf(pdf_path, text_content=content)

    extracted_text = extract_text(str(pdf_path))
    assert content in extracted_text


def test_extract_text_from_empty_pdf_returns_empty_string(tmp_path):
    """Testa se um PDF com uma página em branco (sem texto) retorna string vazia."""
    pdf_path = tmp_path / "blank.pdf"
    _create_pdf(pdf_path, text_content=None)
    assert extract_text(str(pdf_path)) == ""


def test_non_existent_pdf_file_path_returns_empty_string(tmp_path):
    """Testa se o caminho para um arquivo PDF inexistente retorna string vazia."""
    pdf_path = tmp_path / "non_existent.pdf"
    assert extract_text(str(pdf_path)) == ""


def test_path_not_ending_in_pdf_is_not_processed_as_pdf(tmp_path):
    """Testa se um arquivo que não termina em .pdf não é processado como PDF."""
    file_path = tmp_path / "document.log"
    _create_pdf(file_path, text_content="Conteúdo secreto")
    assert extract_text(str(file_path)) == str(file_path)


def test_corrupted_pdf_file_returns_empty_string(tmp_path):
    """Testa se um arquivo PDF corrompido retorna uma string vazia."""
    pdf_path = tmp_path / "corrupted.pdf"
    pdf_path.write_text("%PDF-1.x\n...junk...\n")
    assert extract_text(str(pdf_path)) == ""
