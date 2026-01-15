import re
from typing import Optional, Callable, List

# Define um tipo para uma etapa de pré-processamento para clareza e extensibilidade.
ProcessingStep = Callable[[str], str]


def _to_lowercase(text: str) -> str:
    """Converte a string para minúsculas."""
    return text.lower()


def _remove_control_characters(text: str) -> str:
    """Remove caracteres de controle, mas preserva espaços em branco importantes (tab, newline)."""
    # Remove caracteres do bloco C0, exceto tab (\x09), newline (\x0a) e carriage return (\x0d).
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)


def _normalize_whitespace(text: str) -> str:
    """Substitui múltiplos espaços e tabs por um único espaço e remove espaços no início/fim."""
    # Substitui múltiplos espaços/tabs por um único espaço.
    processed_text = re.sub(r'[ \t]+', ' ', text)
    # Remove espaços em branco (incluindo quebras de linha) das extremidades.
    return processed_text.strip()


class TextPreprocessor:
    """
    Encapsula um pipeline de pré-processamento de texto.

    Esta estrutura permite que novas etapas de processamento sejam facilmente
    adicionadas ou que o pipeline seja reconfigurado no futuro.
    """

    def __init__(self, steps: Optional[List[ProcessingStep]] = None):
        """
        Inicializa o pré-processador com uma lista de etapas.

        Args:
            steps: Uma lista opcional de funções de processamento. Se não for
                   fornecido, usa um pipeline padrão de limpeza básica.
        """
        if steps is None:
            # Pipeline padrão com as funcionalidades mínimas solicitadas
            self.steps = [
                _to_lowercase,
                _remove_control_characters,
                _normalize_whitespace,
            ]
        else:
            self.steps = steps

    def process(self, text: str) -> str:
        """
        Aplica todas as etapas de pré-processamento à string de entrada.

        Args:
            text: O texto a ser processado.

        Returns:
            O texto após a aplicação de todas as etapas do pipeline.
        """
        processed_text = text
        for step in self.steps:
            processed_text = step(processed_text)
        return processed_text


# Instância padrão pronta para ser importada e usada em outros módulos.
_default_preprocessor = TextPreprocessor()

def preprocess_text(text: Optional[str]) -> str:
    """
    Função pública para pré-processar um texto usando o pipeline padrão.

    Esta função serve como um ponto de entrada simples e direto para a
    funcionalidade de pré-processamento.

    Args:
        text: A string de entrada a ser processada, ou None.

    Returns:
        O texto limpo e normalizado. Retorna uma string vazia para entradas inválidas.
    """
    if not isinstance(text, str):
        return ""
    
    return _default_preprocessor.process(text)
