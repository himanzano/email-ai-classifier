import pytest
import json
from unittest.mock import patch, MagicMock
from app.services.classifier import (
    classify_email,
    _validate_classification_response,
    InvalidResponseJsonError,
    InvalidClassificationResponseError
)

# --- Mocks e Fixtures ---

VALID_JSON_RESPONSE = {
    "category": "Produtivo",
    "confidence": 0.95,
    "reason": "O e-mail solicita uma ação clara de revisão de documento."
}

@pytest.fixture
def mock_dependencies():
    """
    Fixture que mocka as duas dependências externas de `classify_email`:
    1. `_load_prompt`: Evita a necessidade de ler um arquivo real do disco.
    2. `GenerativeModel`: Evita a chamada de rede para a API Vertex AI.
    """
    with patch('app.services.classifier._load_prompt') as mock_load_prompt, \
         patch('app.services.classifier.GenerativeModel') as mock_model_class:
        
        # Configura o mock do prompt
        mock_load_prompt.return_value = "Prompt base com placeholder: <<<EMAIL_TEXT>>>"
        
        # Configura o mock da API para retornar uma resposta JSON válida por padrão
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value.text = json.dumps(VALID_JSON_RESPONSE)
        mock_model_class.return_value = mock_model_instance
        
        yield mock_load_prompt, mock_model_class

# --- Testes Unitários ---

class TestClassifyEmailUnit:
    """Testa a lógica principal do serviço `classify_email` com dependências mockadas."""

    def test_successful_classification(self, mock_dependencies):
        """
        Verifica se a função processa corretamente uma resposta válida da API.
        """
        mock_load_prompt, mock_model_class = mock_dependencies
        email_text = "Por favor, revise o contrato."

        # Act
        result = classify_email(email_text)

        # Assert
        assert result == VALID_JSON_RESPONSE
        
        # Verifica se as dependências foram chamadas corretamente
        mock_load_prompt.assert_called_once()
        mock_model_instance = mock_model_class.return_value
        mock_model_instance.generate_content.assert_called_once()
        
        # Verifica se o e-mail foi injetado no prompt
        final_prompt = mock_model_instance.generate_content.call_args[0][0]
        assert email_text in final_prompt

    def test_raises_error_on_non_json_response(self, mock_dependencies):
        """
        Verifica se `InvalidResponseJsonError` é lançado se a API retornar texto não-JSON.
        """
        _, mock_model_class = mock_dependencies
        mock_model_instance = mock_model_class.return_value
        mock_model_instance.generate_content.return_value.text = "Isto não é um JSON."

        with pytest.raises(InvalidResponseJsonError, match="A resposta da API não pôde ser decodificada como JSON"):
            classify_email("Qualquer texto")

    def test_raises_error_on_invalid_schema_response(self, mock_dependencies):
        """
        Verifica se `InvalidClassificationResponseError` é lançado para um JSON com schema incorreto.
        """
        _, mock_model_class = mock_dependencies
        mock_model_instance = mock_model_class.return_value
        # Resposta JSON válida, mas sem a chave 'category'
        invalid_schema = {"confidence": 0.9, "reason": "Falta a categoria."
        }
        mock_model_instance.generate_content.return_value.text = json.dumps(invalid_schema)

        with pytest.raises(InvalidClassificationResponseError, match="não contém as chaves necessárias"):
            classify_email("Qualquer texto")


class TestValidateClassificationResponse:
    """Testa a lógica de validação da resposta em `_validate_classification_response`."""

    def test_passes_on_valid_data(self):
        """Garante que nenhuma exceção é lançada para dados válidos."""
        try:
            _validate_classification_response(VALID_JSON_RESPONSE)
        except InvalidClassificationResponseError:
            pytest.fail("Uma resposta válida não deveria lançar uma exceção de validação.")

    @pytest.mark.parametrize("missing_key", ["category", "confidence", "reason"])
    def test_fails_on_missing_keys(self, missing_key):
        """
        Verifica se a validação falha se uma chave obrigatória estiver faltando.
        """
        invalid_data = VALID_JSON_RESPONSE.copy()
        del invalid_data[missing_key]

        with pytest.raises(InvalidClassificationResponseError, match="não contém as chaves necessárias"):
            _validate_classification_response(invalid_data)

    def test_fails_on_invalid_category_value(self):
        """
        Verifica se a validação falha para um valor de 'category' inválido.
        """
        invalid_data = VALID_JSON_RESPONSE.copy()
        invalid_data["category"] = "Neutro"  # Valor não permitido

        with pytest.raises(InvalidClassificationResponseError, match="O valor de 'category' .* é inválido"):
            _validate_classification_response(invalid_data)

    @pytest.mark.parametrize("invalid_confidence", [
        "alto",  # Tipo errado
        -0.5,    # Fora do range
        1.1,     # Fora do range
        None     # Tipo errado
    ])
    def test_fails_on_invalid_confidence_value(self, invalid_confidence):
        """
        Verifica se a validação falha para valores de 'confidence' inválidos.
        """
        invalid_data = VALID_JSON_RESPONSE.copy()
        invalid_data["confidence"] = invalid_confidence

        with pytest.raises(InvalidClassificationResponseError, match="O valor de 'confidence' .* é inválido"):
            _validate_classification_response(invalid_data)
