import os
from typing import Set

from vertexai.generative_models import GenerativeModel, GenerationConfig

# --- Configurações e Constantes ---

MODEL_NAME = "gemini-2.5-flash"
VALID_CATEGORIES: Set[str] = {"Produtivo", "Improdutivo"}

PROMPT_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")
EMAIL_RESPONDER_PROMPT_PATH = os.path.join(PROMPT_DIR, "email_responder.prompt")


# --- Erros Personalizados ---


class InvalidGeneratedResponseError(ValueError):
    """Lançado quando a resposta gerada pela IA falha nas validações de qualidade."""

    pass


# --- Funções Auxiliares ---


def _load_prompt(prompt_path: str) -> str:
    """Carrega o conteúdo do arquivo de prompt especificado."""
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de prompt não encontrado: {prompt_path}")


def _validate_generated_response(response_text: str, original_text: str) -> None:
    """
    Valida a qualidade e segurança da resposta gerada.

    Args:
        response_text: O texto gerado pelo modelo.
        original_text: O texto do e-mail original (para verificação de eco).

    Raises:
        InvalidGeneratedResponseError: Se a resposta for considerada inválida.
    """
    # 1. Validação de conteúdo vazio ou muito curto
    if not response_text or len(response_text.strip()) < 10:
        raise InvalidGeneratedResponseError(
            "A resposta gerada está vazia ou é muito curta."
        )

    # 2. Validação de comprimento excessivo
    if len(response_text) > 2000:
        raise InvalidGeneratedResponseError(
            "A resposta gerada excede o limite de segurança."
        )

    # 3. Validação de alucinações de personagem (frases de modelo de linguagem)
    forbidden_phrases = [
        "como modelo de linguagem",
        "sou uma ia",
        "não consigo",
        "não posso",
    ]
    normalized_response = response_text.lower()
    if any(phrase in normalized_response for phrase in forbidden_phrases):
        raise InvalidGeneratedResponseError(
            f"A resposta contém frases proibidas de IA: '{response_text}'"
        )

    # 4. Validação de eco (repetição do e-mail original)
    # Se mais de 30% do e-mail original estiver contido na resposta, provavelmente é um eco
    if len(original_text) > 50 and original_text[:50].lower() in normalized_response:
        raise InvalidGeneratedResponseError(
            "A resposta parece repetir o início do e-mail original."
        )


def _clean_response(text: str) -> str:
    """Normaliza a resposta removendo formatação indesejada."""
    text = text.strip()

    # Remove blocos de código markdown se o modelo insistir em colocá-los
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("\n", 1)[0]

    # Remove prefixos comuns de chat (ex: "Assunto:", "Resposta:")
    text = text.replace("Assunto:", "").replace("Resposta:", "").strip()

    return text


# --- Serviço Principal ---


def generate_response(email_text: str, category: str) -> str:
    """
    Gera uma resposta de e-mail usando o modelo Gemini com base na categoria.

    Args:
        email_text: O corpo do e-mail original.
        category: A classificação do e-mail ('Produtivo' ou 'Improdutivo').

    Returns:
        O corpo do e-mail de resposta gerado.

    Raises:
        ValueError: Se os parâmetros de entrada forem inválidos.
        FileNotFoundError: Se o arquivo de prompt não for encontrado.
        InvalidGeneratedResponseError: Se a resposta gerada não for segura/válida.
    """
    # Validação de Entrada
    if not email_text or not email_text.strip():
        raise ValueError("O texto do e-mail não pode ser vazio.")

    # Normalização e validação da categoria
    # A comparação é case-insensitive para robustez, mas passamos a versão correta pro prompt
    normalized_category = category.strip().capitalize()
    if normalized_category not in VALID_CATEGORIES:
        # Tenta mapear ou falha. Aqui optamos por ser estritos para evitar erros silenciosos.
        # Se a categoria for desconhecida, o prompt pode se comportar de forma imprevisível.
        raise ValueError(
            f"Categoria inválida: '{category}'. Esperado: {VALID_CATEGORIES}"
        )

    # Carregamento e Preparação do Prompt
    prompt_template = _load_prompt(EMAIL_RESPONDER_PROMPT_PATH)

    # Interpolação Segura
    prompt = prompt_template.replace("<<<EMAIL_CATEGORY>>>", normalized_category)
    prompt = prompt.replace("<<<EMAIL_TEXT>>>", email_text)

    # Configuração do Modelo
    model = GenerativeModel(MODEL_NAME)
    generation_config = GenerationConfig(
        temperature=0.2,  # Baixa criatividade para garantir profissionalismo e seguir regras
        max_output_tokens=2500,
        top_p=0.8,
        top_k=40,
    )

    # Chamada ao Modelo
    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        generated_text = response.text
    except Exception as e:
        # Encapsula erros da API para facilitar o tratamento no nível superior
        raise RuntimeError(f"Erro ao comunicar com o modelo Gemini: {e}") from e

    # Pós-processamento e Validação
    cleaned_text = _clean_response(generated_text)
    _validate_generated_response(cleaned_text, email_text)

    return cleaned_text
