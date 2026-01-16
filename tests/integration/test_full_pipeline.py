import os
import pytest
from app.services.classifier import classify_email
from app.utils.text_extractor import extract_text
from app.utils.preprocess import preprocess_text

# --- Cenários de Teste para o Pipeline de Classificação Completo ---

EMAIL_PIPELINE_CASES = [
    pytest.param(
        # Conteúdo Bruto do E-mail (com HTML)
        """
        <p><b>URGENTE:</b> O deploy para produção falhou.</p>
        <p>O sistema de pagamentos está instável devido a um erro de autenticação no ambiente XPT-03.
        A fatura de R$ 1.500,00 de um cliente importante foi afetada.</p>
        <p>Precisamos de uma análise imediata. Aguardo retorno.</p>
        """,
        # Categoria Esperada (para verificação de consistência)
        "Produtivo",
        # ID do Teste
        id="productive_urgent_system_failure_html"
    ),
    pytest.param(
        "Lembrete: sua reunião de acompanhamento semanal do projeto 'Atlas' começa em 15 minutos. Link na descrição.",
        "Improdutivo",
        id="improductive_meeting_reminder_plain"
    ),
    pytest.param(
        """
        <h1>Sua compra foi confirmada!</h1>
        <p>Olá, seu pedido nº 789-ABC foi confirmado e já está sendo preparado para o envio.</p>
        <p>Nenhuma ação é necessária de sua parte. Agradecemos a preferência!</p>
        """,
        "Improdutivo",
        id="improductive_order_confirmation_html"
    ),
    pytest.param(
        "Colegas, poderiam por favor revisar a documentação da nova API de pagamentos? O prazo para feedback é amanhã, e a opinião de vocês é fundamental para a aprovação final do documento.",
        "Produtivo",
        id="productive_document_review_request_plain"
    ),
    pytest.param(
        "Apenas para informar: a manutenção programada no servidor de DEV ocorrerá neste sábado, das 2h às 4h da manhã. O ambiente ficará indisponível durante essa janela.",
        "Improdutivo",
        id="improductive_maintenance_warning_plain"
    ),
]

# --- Condições para Pular os Testes de Integração ---

RUN_INTEGRATION_TESTS = os.getenv("RUN_INTEGRATION_TESTS", "false").lower() == "true"
GCP_CONFIG_IS_SET = all(os.getenv(var) for var in ["GCP_PROJECT_ID", "GCP_LOCATION"])
SKIP_REASON = (
    "Teste de integração com Vertex AI requer RUN_INTEGRATION_TESTS=true, "
    "autenticação ADC e as variáveis GCP_PROJECT_ID e GCP_LOCATION."
)

# --- Teste de Integração de Pipeline Completo ---

@pytest.mark.integration
@pytest.mark.skipif(not (RUN_INTEGRATION_TESTS and GCP_CONFIG_IS_SET), reason=SKIP_REASON)
@pytest.mark.parametrize("raw_email_content, expected_category", EMAIL_PIPELINE_CASES)
def test_full_classification_pipeline(raw_email_content, expected_category):
    """
    Executa um teste de integração de ponta a ponta, simulando o fluxo completo:
    1. Extração de texto de conteúdo bruto (HTML ou texto plano).
    2. Pré-processamento do texto (remoção de stopwords, lematização, etc.).
    3. Classificação via Vertex AI (Gemini).
    4. Validação do schema da resposta e da consistência da categoria.
    """
    # Etapa 1: Extrair texto puro do conteúdo bruto.
    text = extract_text(raw_email_content)
    assert text and text.strip(), "A extração de texto não deveria resultar em uma string vazia."

    # Etapa 2: Pré-processar o texto extraído.
    processed_text = preprocess_text(
        text,
        remove_stopwords=True,
        lemmatize=True,
        normalize_numbers=True
    )
    assert processed_text and processed_text.strip(), "O pré-processamento não deveria resultar em uma string vazia."

    # Etapa 3: Executar a chamada real à API com o texto pré-processado.
    try:
        response = classify_email(processed_text)
    except Exception as e:
        pytest.fail(
            f"A chamada de integração ao Vertex AI falhou inesperadamente para o caso '{expected_category}'. "
            f"Verifique a autenticação e as configurações. Erro: {e}"
        )

    # Etapa 4: Validar o contrato e a consistência da resposta da API.
    assert response is not None, "A resposta da API não pode ser nula."
    assert "category" in response, "A resposta deve conter a chave 'category'."
    assert response["category"] in {"Produtivo", "Improdutivo"}, \
        f"A categoria '{response['category']}' não é um valor válido."
    
    assert "confidence" in response, "A resposta deve conter a chave 'confidence'."
    assert isinstance(response["confidence"], (float, int)), "A confiança deve ser um número."
    assert 0.0 <= response["confidence"] <= 1.0, "O valor de confiança deve estar entre 0.0 e 1.0."

    assert "reason" in response and isinstance(response["reason"], str) and response["reason"], \
        "A resposta deve conter uma justificativa (reason) em string e não-vazia."

    # Validação de consistência: Para exemplos claros, a categoria deve ser a esperada.
    # Isso atua como um "teste de fumaça" para a lógica do prompt e do modelo.
    assert response["category"] == expected_category, (
        f"Falha de consistência no teste '{expected_category}'. "
        f"Modelo retornou '{response['category']}'. Justificativa: '{response['reason']}'"
    )
