import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

# --- Condições para Pular o Teste de Integração Real ---

USE_REAL_GEMINI = os.getenv("USE_REAL_GEMINI", "false").lower() == "true"
GCP_IS_CONFIGURED = all(os.getenv(var) for var in ["GCP_PROJECT_ID", "GCP_LOCATION"])

SKIP_REASON = (
    "Teste de integração da API com IA real requer USE_REAL_GEMINI=true e "
    "configuração do GCP (PROJECT_ID, LOCATION, ADC)."
)

@pytest.fixture
def client():
    """Fixture que fornece um cliente de teste para a aplicação FastAPI."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.mark.integration
@patch('app.api.classify.classify_email', return_value={"category": "Produtivo", "confidence": 0.9, "reason": "Mock"})
@patch('app.api.classify.generate_response', return_value="Resposta mockada.")
def test_api_classify_integration_with_mocked_ai(mock_generate, mock_classify, client):
    """
    Teste de integração da API: valida o fluxo HTTP e a orquestração
    dos serviços com a IA mockada. É o teste padrão em CI.
    """
    response = client.post("/api/process-email", data={"email_content": "Olá, revise o anexo."})
    
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Produtivo"
    assert data["response"] == "Resposta mockada."
    mock_classify.assert_called_once()
    mock_generate.assert_called_once()

@pytest.mark.integration
@pytest.mark.skipif(not USE_REAL_GEMINI or not GCP_IS_CONFIGURED, reason=SKIP_REASON)
def test_api_classify_integration_with_real_ai(client):
    """
    Teste de integração E2E: faz uma chamada real ao Vertex AI.
    Só executa se a flag USE_REAL_GEMINI=true estiver ativa.
    """
    email_text = "Por favor, revise o relatório de vendas e aprove o orçamento até o final do dia."
    
    response = client.post("/api/process-email", data={"email_content": email_text})
    
    assert response.status_code == 200
    data = response.json()
    
    # Validações de schema
    assert "category" in data
    assert data["category"] in {"Produtivo", "Improdutivo"}
    assert "response" in data and data["response"]
    assert len(data["response"]) > 20
