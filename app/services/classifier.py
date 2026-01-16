import os
import json
from typing import Dict

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# --- Configuração do Vertex AI ---_ 
# O ID do projeto e a localização são obtidos de variáveis de ambiente para
# garantir portabilidade entre ambientes (local, dev, prod).
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
MODEL_NAME = "gemini-2.5-pro"

# Inicializa o Vertex AI SDK. A autenticação é tratada automaticamente
# pelo ambiente (gcloud auth application-default login, variáveis de ambiente, etc.).
vertexai.init(project=PROJECT_ID, location=LOCATION)


# --- Constantes e Caminhos ---
PROMPT_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")
EMAIL_CLASSIFIER_PROMPT_PATH = os.path.join(PROMPT_DIR, "email_classifier.prompt")


# --- Erros Personalizados ---
class InvalidResponseJsonError(ValueError):
    """Lançado quando a resposta da API não é um JSON válido."""
    pass

class InvalidClassificationResponseError(ValueError):
    """Lançado quando o JSON da resposta não segue o schema esperado."""
    pass


# --- Funções Auxiliares ---

def _load_prompt(prompt_path: str) -> str:
    """Carrega o conteúdo de um arquivo de prompt."""
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de prompt não encontrado em: {prompt_path}")

def _validate_classification_response(response_data: Dict) -> None:
    """
    Valida o schema e os valores da resposta de classificação.
    Lança uma exceção se a validação falhar.
    """
    required_keys = {"category", "confidence", "reason"}
    if not required_keys.issubset(response_data.keys()):
        raise InvalidClassificationResponseError(f"A resposta JSON não contém as chaves necessárias: {required_keys}")

    category = response_data.get("category")
    if category not in ["Produtivo", "Improdutivo"]:
        raise InvalidClassificationResponseError(f"O valor de 'category' ('{category}') é inválido. Esperado: 'Produtivo' ou 'Improdutivo'.")

    confidence = response_data.get("confidence")
    if not isinstance(confidence, (float, int)) or not (0.0 <= confidence <= 1.0):
        raise InvalidClassificationResponseError(f"O valor de 'confidence' ('{confidence}') é inválido. Esperado: float entre 0.0 e 1.0.")


# --- Serviço de Classificação ---

def classify_email(text: str) -> Dict:
    """
    Classifica o texto de um e-mail como 'Produtivo' ou 'Improdutivo' usando o Gemini.

    Args:
        text: O conteúdo de texto do e-mail a ser classificado.

    Returns:
        Um dicionário com a classificação, confiança e a justificativa.
    
    Raises:
        InvalidResponseJsonError: Se a resposta da API não for um JSON válido.
        InvalidClassificationResponseError: Se o JSON da resposta for inválido.
        FileNotFoundError: Se o arquivo de prompt não for encontrado.
    """
    # 1. Carregar e formatar o prompt
    prompt_template = _load_prompt(EMAIL_CLASSIFIER_PROMPT_PATH)
    prompt = prompt_template.replace("<<<EMAIL_TEXT>>>", text)

    # 2. Chamar a API do Gemini
    model = GenerativeModel(MODEL_NAME)
    generation_config = GenerationConfig(
        temperature=0.0,  # Baixa temperatura para respostas mais determinísticas e consistentes
        response_mime_type="application/json",
    )
    
    response = model.generate_content(prompt, generation_config=generation_config)
    
    # 3. Extrair e fazer o parse da resposta
    try:
        # A resposta do Gemini com mime_type="application/json" já é um objeto JSON
        # mas o SDK pode envolvê-la. O texto puro é a representação mais segura.
        response_text = response.text.strip()
        response_data = json.loads(response_text)
    except (json.JSONDecodeError, AttributeError) as e:
        raise InvalidResponseJsonError(f"A resposta da API não pôde ser decodificada como JSON. Resposta: {response.text}") from e

    # 4. Validar e retornar a resposta
    _validate_classification_response(response_data)
    
    return response_data
