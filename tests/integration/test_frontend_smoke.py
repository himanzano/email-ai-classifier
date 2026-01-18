import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Fixture que fornece um cliente de teste para a aplicação FastAPI."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.mark.integration
def test_get_root_serves_html(client):
    """
    Verifica se a rota raiz (GET /) retorna um HTML com sucesso.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

@pytest.mark.integration
def test_root_html_contains_key_elements(client):
    """
    Smoke test: verifica se o HTML servido contém os elementos essenciais da UI.
    Isso confirma que o arquivo correto está sendo renderizado, sem testar o layout.
    """
    response = client.get("/")
    html_content = response.text
    
    assert 'id="email-content"' in html_content
    assert 'id="process-email-btn"' in html_content
    assert 'id="results-section"' in html_content
    assert 'Classificador de Emails com IA' in html_content
