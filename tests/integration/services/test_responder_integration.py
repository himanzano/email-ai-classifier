import os
import pytest
from app.services.responder import generate_response

# --- Condições para Pular o Teste de Integração ---

RUN_INTEGRATION_TESTS = os.getenv("RUN_INTEGRATION_TESTS", "false").lower() == "true"
GCP_IS_CONFIGURED = all(
    os.getenv(var)
    for var in ["GCP_PROJECT_ID", "GCP_LOCATION", "GOOGLE_APPLICATION_CREDENTIALS"]
)

SKIP_REASON = (
    "Teste de integração do responder requer RUN_INTEGRATION_TESTS=true e as variáveis "
    "de ambiente do GCP (PROJECT_ID, LOCATION, GOOGLE_APPLICATION_CREDENTIALS)."
)

# --- Teste de Integração ---


@pytest.mark.integration
@pytest.mark.skipif(
    not (RUN_INTEGRATION_TESTS and GCP_IS_CONFIGURED), reason=SKIP_REASON
)
@pytest.mark.parametrize("category", ["Produtivo", "Improdutivo"])
def test_generate_response_vertex_ai_integration(category):
    """
    Executa uma chamada real ao Vertex AI para validar a geração de resposta.

    Este teste verifica se, para ambas as categorias:
    1. A autenticação ADC funciona.
    2. O prompt é aceito pela API do Gemini.
    3. A resposta gerada pelo modelo passa nas validações de qualidade do nosso serviço.
    """
    # Arrange: Um texto de e-mail genérico para dar contexto à IA.
    email_text = (
        "Assunto: Status do Projeto XPTO\n\n"
        "Olá, apenas para informar que a fase 2 foi concluída. "
        "A documentação foi atualizada no Confluence. "
        "Seguimos para a fase 3 na próxima sprint."
    )

    # Act: Tenta gerar a resposta, fazendo uma chamada real à API.
    try:
        response = generate_response(email_text=email_text, category=category)
    except Exception as e:
        pytest.fail(
            f"A chamada de integração do responder para a categoria '{category}' falhou. "
            f"Verifique a autenticação e as configurações. Erro: {type(e).__name__}: {e}"
        )

    # Assert: Validações de formato e qualidade (não de conteúdo exato).
    # A própria função `generate_response` já possui validações internas (`_validate_generated_response`).
    # Se ela retornar um valor em vez de lançar uma exceção, significa que as validações passaram.
    # Aqui, apenas garantimos que o retorno não é nulo/vazio.
    assert response, "A resposta gerada não pode ser nula ou vazia."
    assert isinstance(response, str), "O tipo de retorno deve ser uma string."
    assert len(response) > 20, (
        "A resposta gerada deve ter um comprimento mínimo razoável."
    )
