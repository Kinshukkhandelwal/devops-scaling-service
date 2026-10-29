import os
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    API_TOKEN: str = os.getenv("API_TOKEN", "nerdy-secret-token-123")
    FIXTURES_DIR: Path = Path(os.getenv("FIXTURES_DIR", BASE_DIR / "fixtures"))
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "double") # 'double' for offline deterministic test runner
    LLM_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")

settings = Settings()
