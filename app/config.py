import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    asr_url: str = "http://127.0.0.1:8000/v1/audio/transcriptions"
    llm_url: str = "http://127.0.0.1:8000/v1/chat/completions"
    asr_model: str = "Qwen3-ASR-1.7B-8bit"
    llm_model: str = "SuperGemma4-31b-abliterated-mlx-4bit"
    meetings_dir: Path = Path.home() / "Documents" / "Meetings"
    port: int = 8080

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
