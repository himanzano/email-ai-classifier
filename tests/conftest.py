from pathlib import Path
from dotenv import load_dotenv


def pytest_configure(config):
    """
    Registra marcadores personalizados para o pytest e configura o ambiente
    carregando variáveis de um arquivo .env.
    """
    # Registrar marcador de integração
    config.addinivalue_line(
        "markers",
        "integration: marca um teste como um teste de integração, que pode fazer chamadas reais a serviços externos.",
    )

    # Carregar variáveis de ambiente do .env
    base_dir = Path(__file__).resolve().parent.parent
    env_path = base_dir / ".env"
    load_dotenv(dotenv_path=env_path)
