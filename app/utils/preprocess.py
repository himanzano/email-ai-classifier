import re
from typing import Optional, Callable, List, Dict, Set

# --- Stopwords (Extensível para múltiplos idiomas) ---

_STOPWORDS_PT: Set[str] = {
    'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não',
    'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi',
    'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito',
    'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso',
    'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem',
    'nas', 'me', 'esse', 'eles', 'estão', 'você', 'tinha', 'foram', 'essa', 'num',
    'nem', 'suas', 'meu', 'às', 'minha', 'numa', 'pelos', 'elas', 'havia', 'seja',
    'qual', 'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 'esses', 'pelas',
    'este', 'fosse', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas',
    'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela',
    'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas',
    'isto', 'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive', 'esteve',
    'estivemos', 'estiveram', 'estava', 'estávamos', 'estavam', 'estivera',
    'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos',
    'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há', 'havemos',
    'hão', 'houve', 'houvemos', 'houveram', 'houvera', 'houvéramos', 'haja',
    'hajamos', 'hajam', 'houvesse', 'houvéssemos', 'houvessem', 'houver',
    'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão',
    'houveria', 'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 'éramos',
    'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos',
    'sejam', 'fosse', 'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei',
    'será', 'seremos', 'serão', 'seria', 'seríamos', 'seriam', 'tenho', 'tem',
    'temos', 'tém', 'tinha', 'tínhamos', 'tinham', 'tive', 'teve', 'tivemos',
    'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse',
    'tivéssemos', 'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei', 'terá',
    'teremos', 'terão', 'teria', 'teríamos', 'teriam',
}

_STOPWORD_LISTS: Dict[str, Set[str]] = {
    "pt": _STOPWORDS_PT,
}

# --- Etapas de Pré-processamento ---

ProcessingStep = Callable[[str], str]

def _to_lowercase(text: str) -> str:
    return text.lower()

def _remove_control_characters(text: str) -> str:
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

def _normalize_whitespace(text: str) -> str:
    processed_text = re.sub(r'[ \t]+', ' ', text)
    return processed_text.strip()

def _remove_stopwords(text: str, stopwords: Set[str]) -> str:
    words = text.split(' ')
    filtered_words = [word for word in words if word not in stopwords]
    return ' '.join(filtered_words)

# --- Pipeline de Pré-processamento ---

class TextPreprocessor:
    """
    Encapsula e executa um pipeline de pré-processamento de texto.
    """
    def __init__(self, base_steps: Optional[List[ProcessingStep]] = None, stopword_lists: Optional[Dict[str, Set[str]]] = None):
        self.base_steps = base_steps or [
            _to_lowercase,
            _remove_control_characters,
            _normalize_whitespace,
        ]
        self.stopword_lists = stopword_lists or _STOPWORD_LISTS

    def process(self, text: str, remove_stopwords: bool = False, lang: str = 'pt') -> str:
        """
        Aplica o pipeline de processamento, com opção de remover stopwords.
        """
        processed_text = text
        for step in self.base_steps:
            processed_text = step(processed_text)

        if remove_stopwords:
            stopwords_to_remove = self.stopword_lists.get(lang)
            if stopwords_to_remove:
                processed_text = _remove_stopwords(processed_text, stopwords_to_remove)
        
        return processed_text

# --- Função Pública ---

_default_preprocessor = TextPreprocessor()

def preprocess_text(text: Optional[str], remove_stopwords: bool = False) -> str:
    """
    Função pública para pré-processar um texto usando o pipeline padrão.

    Args:
        text: A string de entrada a ser processada, ou None.
        remove_stopwords: Se True, remove as stopwords do idioma padrão (pt).

    Returns:
        O texto limpo e normalizado.
    """
    if not isinstance(text, str):
        return ""
    
    return _default_preprocessor.process(text, remove_stopwords=remove_stopwords)