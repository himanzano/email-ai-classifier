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

# --- Lematização Heurística Simplificada ---
# NOTA: Esta é uma implementação básica e heurística de lematização,
# focada em sufixos comuns do português. Não substitui uma biblioteca
# completa de NLP (como NLTK ou spaCy), mas evita dependências externas.
# Foi projetada para ser simples, previsível e extensível.

def _lemmatize_token_pt(token: str) -> str:
    """
    Aplica regras simples e heurísticas de lematização para um token em português.
    A ordem é importante: regras mais específicas devem vir antes.
    """
    # Regra para plurais em '-es' (ex: autores -> autor, flores -> flor).
    # É mais específica que a regra do '-s', por isso vem primeiro.
    if len(token) > 4 and token.endswith('es'):
        return token[:-2]

    # Regra para plurais simples terminados em 's' (ex: carros -> carro, testes -> teste).
    if len(token) > 3 and token.endswith('s'):
        return token[:-1]

    # Nenhuma regra correspondeu, retorna o token original.
    return token

_LEMMATIZER_FUNCTIONS: Dict[str, Callable[[str], str]] = {
    "pt": _lemmatize_token_pt,
}

def _lemmatize_text(text: str, lang: str = 'pt') -> str:
    """
    Aplica a lematização em todo o texto, token por token, usando a função
    apropriada para o idioma e preservando a pontuação final de cada token.
    """
    lemmatizer = _LEMMATIZER_FUNCTIONS.get(lang)
    if not lemmatizer or not text:
        return text

    words = text.split(' ')
    lemmatized_words = []
    for word in words:
        # Isola a palavra da pontuação final usando regex
        match = re.match(r'^(\w+)([\W_]*)$', word)
        if match:
            token, punctuation = match.groups()
            lemmatized_token = lemmatizer(token)
            lemmatized_words.append(lemmatized_token + punctuation)
        else:
            # Se não houver correspondência (ex: uma string de pontuação pura), mantém o original
            lemmatized_words.append(word)

    return ' '.join(lemmatized_words)


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

    def process(self, text: str, remove_stopwords: bool = False, lang: str = 'pt', lemmatize: bool = False) -> str:
        """
        Aplica o pipeline de processamento, com opção de remover stopwords e lematizar.
        """
        processed_text = text
        for step in self.base_steps:
            processed_text = step(processed_text)

        if remove_stopwords:
            stopwords_to_remove = self.stopword_lists.get(lang)
            if stopwords_to_remove:
                processed_text = _remove_stopwords(processed_text, stopwords_to_remove)
        
        if lemmatize:
            processed_text = _lemmatize_text(processed_text, lang=lang)

        return processed_text

# --- Função Pública ---

_default_preprocessor = TextPreprocessor()

def preprocess_text(text: Optional[str], remove_stopwords: bool = False, lemmatize: bool = False) -> str:
    """
    Função pública para pré-processar um texto usando o pipeline padrão.

    Args:
        text: A string de entrada a ser processada, ou None.
        remove_stopwords: Se True, remove as stopwords do idioma padrão (pt).
        lemmatize: Se True, aplica lematização heurística ao texto.

    Returns:
        O texto limpo, normalizado e opcionalmente lematizado.
    """
    if not isinstance(text, str):
        return ""
    
    return _default_preprocessor.process(text, remove_stopwords=remove_stopwords, lemmatize=lemmatize)
