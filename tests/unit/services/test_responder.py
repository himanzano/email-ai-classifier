import pytest
from unittest.mock import patch, MagicMock
from app.services.responder import (
    generate_response,
    _validate_generated_response,
    InvalidGeneratedResponseError,
    CATEGORY_PROMPTS
)

# Mock da resposta da API Gemini para ser usado nos testes
MOCK_API_RESPONSE = "Esta é uma resposta padrão gerada pelo mock da API."

@pytest.fixture
def mock_vertex_ai():
    """
    Fixture que mocka a chamada à API Vertex AI (GenerativeModel).

    Isso isola os testes da rede e de serviços externos, permitindo a verificação
    da lógica interna do `generate_response` (montagem de prompt, validação, etc.).
    """
    with patch('app.services.responder.GenerativeModel') as mock_model_class:
        # Configura a instância mockada para retornar um objeto com o atributo 'text'
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = MOCK_API_RESPONSE
        mock_model_class.return_value = mock_instance
        yield mock_model_class

class TestGenerateResponseUnit:
    """Testes unitários para a função principal `generate_response`."""

    @pytest.mark.parametrize("category", ["Produtivo", "Improdutivo"])
    def test_selects_correct_prompt_and_calls_api(self, mock_vertex_ai, category):
        """
        Verifica se o prompt correto é montado e se a API é chamada.
        """
        email_text = "Texto de exemplo para o e-mail."
        
        # Act
        response = generate_response(email_text, category)

        # Assert
        # 1. Verifica se a resposta retornada é a esperada do mock
        assert response == MOCK_API_RESPONSE

        # 2. Verifica se o método `generate_content` foi chamado uma vez
        mock_model_instance = mock_vertex_ai.return_value
        mock_model_instance.generate_content.assert_called_once()

        # 3. Inspeciona o prompt enviado para a API
        called_with_prompt = mock_model_instance.generate_content.call_args[0][0]
        assert email_text in called_with_prompt
        assert CATEGORY_PROMPTS[category] in called_with_prompt

    def test_raises_error_for_invalid_category(self, mock_vertex_ai):
        """
        Verifica se uma exceção `ValueError` é lançada para uma categoria desconhecida.
        """
        with pytest.raises(ValueError, match="Categoria de resposta desconhecida: 'Inexistente'"):
            generate_response("Qualquer texto", "Inexistente")
        
        # Garante que a API não foi chamada desnecessariamente
        mock_model_instance = mock_vertex_ai.return_value
        mock_model_instance.generate_content.assert_not_called()

    def test_raises_error_on_invalid_generated_response(self, mock_vertex_ai):
        """
        Verifica se a validação interna é acionada se a API retornar lixo.
        """
        # Configura o mock para retornar uma resposta que falhará na validação
        mock_model_instance = mock_vertex_ai.return_value
        mock_model_instance.generate_content.return_value.text = "inválido"

        with pytest.raises(InvalidGeneratedResponseError, match="A resposta gerada está vazia ou é muito curta."):
            generate_response("Qualquer texto", "Produtivo")


class TestValidateGeneratedResponse:
    """Testes focados na função auxiliar de validação `_validate_generated_response`."""

    @pytest.mark.parametrize("response_text", [
        "   ",  # Apenas espaços
        "",      # Vazio
        "curto", # Muito curto
    ])
    def test_fails_on_empty_or_too_short_response(self, response_text):
        """Valida se a resposta vazia ou curta lança exceção."""
        with pytest.raises(InvalidGeneratedResponseError, match="vazia ou é muito curta"):
            _validate_generated_response(response_text, "original")

    def test_fails_on_too_long_response(self):
        """Valida se a resposta longa lança exceção."""
        long_text = "a" * 1001
        with pytest.raises(InvalidGeneratedResponseError, match="excede o limite de 1000 caracteres"):
            _validate_generated_response(long_text, "original")

    @pytest.mark.parametrize("phrase", ["como modelo de linguagem", "não posso te ajudar"])
    def test_fails_on_forbidden_phrases(self, phrase):
        """Valida se frases proibidas na resposta lançam exceção."""
        response_with_forbidden_phrase = f"Olá, {phrase}, mas posso tentar."
        with pytest.raises(InvalidGeneratedResponseError, match="contém uma frase proibida"):
            _validate_generated_response(response_with_forbidden_phrase, "original")

    def test_fails_on_response_repeating_original_text(self):
        """Valida se a resposta que repete o original lança exceção."""
        original = "Este é o texto original do e-mail que é longo o suficiente para ser detectado como repetido se aparecer na resposta."
        response_text = f"Sua resposta é: {original}"
        with pytest.raises(InvalidGeneratedResponseError, match="repetir o conteúdo do e-mail original"):
            _validate_generated_response(response_text, original)
    
    def test_passes_on_valid_response(self):
        """Garante que nenhuma exceção é lançada para uma resposta válida."""
        try:
            _validate_generated_response("Esta é uma resposta perfeitamente válida e com tamanho adequado.", "original")
        except InvalidGeneratedResponseError:
            pytest.fail("Uma resposta válida não deveria lançar InvalidGeneratedResponseError.")
