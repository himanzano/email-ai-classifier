import pytest
from app.utils.preprocess import preprocess_text

def test_preprocess_with_none_input():
    """Testa se a entrada None retorna uma string vazia."""
    assert preprocess_text(None) == ""

def test_preprocess_with_empty_string():
    """Testa se uma string vazia de entrada resulta em uma string vazia."""
    assert preprocess_text("") == ""

def test_text_is_converted_to_lowercase():
    """Testa se o texto é completamente convertido para minúsculas."""
    assert preprocess_text("TEXTO EM CAIXA ALTA") == "texto em caixa alta"

def test_multiple_spaces_and_tabs_are_normalized():
    """Testa se múltiplos espaços e tabs são substituídos por um único espaço."""
    assert preprocess_text("texto   com\t\tmuitos   espaços") == "texto com muitos espaços"

def test_leading_and_trailing_whitespace_is_removed():
    """Testa se os espaços em branco no início e no fim são removidos."""
    assert preprocess_text("  \n texto com espaços nas pontas \t ") == "texto com espaços nas pontas"

def test_control_characters_are_removed():
    """Testa se caracteres de controle invisíveis são removidos."""
    # Incluindo um backspace (\x08) e um start of heading (\x01)
    assert preprocess_text("texto\x08com\x01controle") == "textocomcontrole"

def test_newlines_are_preserved_within_text():
    """Testa se quebras de linha no meio do texto são mantidas (mas normalizadas)."""
    # O strip() remove as quebras de linha das pontas.
    # A normalização de espaços não afeta as quebras de linha internas.
    input_text = "primeira linha\n\n  segunda linha com espaços"
    expected_text = "primeira linha\n\n segunda linha com espaços"
    assert preprocess_text(input_text) == expected_text

def test_full_preprocessing_pipeline_on_complex_string():
    """Testa o pipeline completo com uma string complexa."""
    input_text = "  \tUM TEXTO\n\n\nCOM\x0cMÚLTIPLOS\x08 PROBLEMAS  \n"
    expected = "um texto\n\n\ncommúltiplos problemas"
    assert preprocess_text(input_text) == expected

def test_preprocessing_is_idempotent():
    """Testa se aplicar o pré-processamento duas vezes dá o mesmo resultado que uma vez."""
    input_text = "  TEXTO \t\tCOM VÁRIOS  \nPROBLEMAS  "
    processed_once = preprocess_text(input_text)
    processed_twice = preprocess_text(processed_once)
    assert processed_once == processed_twice

# --- Testes para Remoção de Stopwords ---

def test_stopwords_are_not_removed_by_default():
    """Testa se as stopwords NÃO são removidas se a opção não for passada."""
    input_text = "este é um teste com stopwords"
    # O comportamento padrão é normalizar, mas não remover.
    expected = "este é um teste com stopwords"
    assert preprocess_text(input_text) == expected
    assert preprocess_text(input_text, remove_stopwords=False) == expected

def test_stopwords_are_removed_when_option_is_true():
    """Testa a remoção básica de stopwords quando a opção é ativada."""
    input_text = "este é um teste com algumas stopwords"
    expected = "teste algumas stopwords"
    assert preprocess_text(input_text, remove_stopwords=True) == expected

def test_text_with_only_stopwords_returns_empty_string():
    """Testa se uma string contendo apenas stopwords resulta em uma string vazia."""
    input_text = "com de para em"
    expected = ""
    assert preprocess_text(input_text, remove_stopwords=True) == expected

def test_stopword_removal_is_case_insensitive():
    """Testa se a remoção de stopwords funciona independentemente da capitalização."""
    # O texto é primeiro convertido para minúsculas, depois as stopwords são removidas.
    input_text = "Este É UM teste"
    expected = "teste"
    assert preprocess_text(input_text, remove_stopwords=True) == expected

def test_stopword_removal_does_not_match_substrings():
    """Testa se a remoção não afeta palavras que contêm stopwords como substrings."""
    # "ser" é uma stopword, mas "série" e "serviço" não devem ser removidas.
    input_text = "gostaria de ser notificado sobre a série e o serviço"
    expected = "gostaria notificado sobre série serviço"
    assert preprocess_text(input_text, remove_stopwords=True) == expected