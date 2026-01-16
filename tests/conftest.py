from pathlib import Path
from dotenv import load_dotenv

def pytest_configure():
    base_dir = Path(__file__).resolve().parent.parent
    env_path = base_dir / ".env"
    load_dotenv(dotenv_path=env_path)
