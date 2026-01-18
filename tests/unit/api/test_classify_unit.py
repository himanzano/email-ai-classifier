import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

# Mock da resposta dos serviços para os testes unitários
MOCK_CLASSIFICATION = {"category": "Produtivo", "confidence": 0.9, "reason": "Mock reason"}
MOCK_RESPONSE = "Esta é uma resposta mockada."

@pytest.fixture
def client():
    """Fixture que fornece um cliente de teste para a aplicação FastAPI."""
    with TestClient(app) as test_client:
        yield test_client

@patch('app.api.classify.extract_text', return_value="Texto extraído.")
@patch('app.api.classify.preprocess_text', return_value="Texto pré-processado.")
@patch('app.api.classify.classify_email', return_value=MOCK_CLASSIFICATION)
@patch('app.api.classify.generate_response', return_value=MOCK_RESPONSE)
def test_process_email_with_text_input_success(
    mock_generate, mock_classify, mock_preprocess, mock_extract, client
):
    """
    Testa o fluxo de sucesso do endpoint com entrada de texto como dado de formulário.
    """
    # Act
    response = client.post("/api/process-email", data={"email_content": "Olá mundo"})

    # Assert
    assert response.status_code == 200
    content = response.text
    # Verifica se os dados processados aparecem no HTML retornado
    assert MOCK_RESPONSE in content
    
    mock_extract.assert_called_once()
    mock_preprocess.assert_called_once()
    mock_classify.assert_called_once()
    mock_generate.assert_called_once()

@patch('app.api.classify.extract_text', return_value="Texto do arquivo.")
@patch('app.api.classify.preprocess_text', return_value="Texto pré-processado.")
@patch('app.api.classify.classify_email', return_value=MOCK_CLASSIFICATION)
@patch('app.api.classify.generate_response', return_value=MOCK_RESPONSE)
def test_process_email_with_file_upload_success(
    mock_generate, mock_classify, mock_preprocess, mock_extract, client
):
    """
    Testa o fluxo de sucesso com upload de arquivo.
    """
    # Arrange
    file_content = b"Conteudo do arquivo de teste."
    
    # Act
    response = client.post(
        "/api/process-email",
        files={"file": ("test.txt", file_content, "text/plain")}
    )

    # Assert
    assert response.status_code == 200
    assert MOCK_RESPONSE in response.text
    mock_extract.assert_called_once()
    mock_classify.assert_called_once()

def test_process_email_fails_with_no_input(client):
    """Verifica se a API retorna 400 se nenhum dado for enviado."""
    response = client.post("/api/process-email")
    assert response.status_code == 400
    assert "Forneça texto ou um arquivo" in response.text

def test_process_email_fails_with_both_inputs(client):
    """Verifica se a API retorna 400 se ambos os inputs forem enviados."""
    response = client.post(
        "/api/process-email",
        data={"email_content": "texto"},
        files={"file": ("test.txt", b"conteudo", "text/plain")}
    )
    assert response.status_code == 400
    assert "Forneça texto ou um arquivo" in response.text

@patch('app.api.classify.classify_email', side_effect=Exception("Falha na IA"))
def test_process_email_handles_service_exception(mock_classify, client):
    """
    Verifica se uma exceção em um dos serviços é capturada e resulta em 500.
    """
    response = client.post("/api/process-email", data={"email_content": "Olá"})
    assert response.status_code == 500
    assert "Ocorreu um erro inesperado" in response.text

