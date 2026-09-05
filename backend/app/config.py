from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict # import para configurar variables de entorno

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings): # la clase Settings hereda de BaseSettings, lo que permite definir variables de entorno y sus valores predeterminados.
    database_url: str

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    enable_ai_reports: bool = False
    ai_report_provider: Literal["openai", "ollama"] = "openai"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, 
        env_file_encoding="utf-8", 
        extra="ignore", 
    )

settings = Settings() 