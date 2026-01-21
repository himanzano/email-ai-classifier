import os
import pytest
from app.services.classifier import classify_email

# --- Teste de Integração para o Classificador com Vertex AI ---


@pytest.mark.integration
def test_classify_email_vertex_ai_integration():
    """
    Executa um teste de integração real contra a API Vertex AI (Gemini).

    Este teste valida o fluxo completo:
    1. A capacidade de autenticar usando Application Default Credentials (ADC).
    2. A correta inicialização do SDK `vertexai`.
    3. O envio de um prompt para o modelo `gemini-2.5-pro`.
    4. A validação do schema da resposta retornada pela API.

    O teste é projetado para ser seguro em ambientes de CI/CD, sendo
    automaticamente ignorado se as condições necessárias não forem atendidas.
    """
    # Condição 1: Pular se a flag explícita não estiver ativa.
    if os.getenv("RUN_INTEGRATION_TESTS", "false").lower() != "true":
        pytest.skip(
            "Teste de integração com Vertex AI ignorado. "
            "Defina RUN_INTEGRATION_TESTS=true para executá-lo."
        )

    # Condição 2: Pular se as variáveis de ambiente do GCP não estiverem definidas.
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION")
    if not project_id or not location:
        pytest.skip(
            "Teste de integração com Vertex AI ignorado. "
            "As variáveis de ambiente GCP_PROJECT_ID e GCP_LOCATION devem ser definidas."
        )

    # Arrange: Um texto de e-mail claramente "Produtivo".
    # O conteúdo é inequívoco para minimizar a chance de uma classificação
    # ambígua ou incorreta do modelo, focando o teste na integração.
    productive_email_text = (
        "Olá equipe, por favor, revisem o contrato em anexo e me enviem "
        "seus comentários até o final da tarde de amanhã. A aprovação de "
        "vocês é necessária para avançarmos com o cliente."
    )

    # Act: Executa a chamada real. Qualquer exceção aqui causará falha.
    try:
        response = classify_email(productive_email_text)
    except Exception as e:
        pytest.fail(
            f"A chamada de integração ao Vertex AI falhou inesperadamente. "
            f"Verifique a autenticação ADC e as configurações do projeto. Erro: {e}"
        )

    # Assert: Valida o contrato da resposta.
    # Não testamos a lógica exata da classificação (ex: `assert response['category'] == 'Produtivo'`),
    # pois o comportamento do LLM pode variar. Em vez disso, validamos que a resposta
    # adere ao schema esperado.
    assert response is not None, "A resposta da API não pode ser nula."
    assert "category" in response, "A resposta deve conter a chave 'category'."
    assert response["category"] in {"Produtivo", "Improdutivo"}, (
        f"A categoria '{response['category']}' não é um valor válido."
    )

    assert "confidence" in response, "A resposta deve conter a chave 'confidence'."
    assert isinstance(response["confidence"], (float, int)), (
        "A confiança deve ser um número."
    )
    assert 0.0 <= response["confidence"] <= 1.0, (
        "O valor de confiança deve estar entre 0.0 e 1.0."
    )

    assert (
        "reason" in response
        and isinstance(response["reason"], str)
        and response["reason"]
    ), "A resposta deve conter uma justificativa (reason) em string e não-vazia."
