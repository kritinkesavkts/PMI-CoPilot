"""
Configuration for Agentic AI PMI Copilot.
Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # LLM
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_provider: str = "openai"

    # Storage
    data_dir: str = "./data"
    max_upload_mb: int = 25

    # App
    app_name: str = "Agentic AI PMI Copilot"
    app_version: str = "0.1.0"
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def upload_dir(self) -> Path:
        p = Path(self.data_dir) / "uploads"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def output_dir(self) -> Path:
        p = Path(self.data_dir) / "outputs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def session_dir(self) -> Path:
        p = Path(self.data_dir) / "sessions"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def prompts_dir(self) -> Path:
        return Path(__file__).parent / "prompts"


settings = Settings()
