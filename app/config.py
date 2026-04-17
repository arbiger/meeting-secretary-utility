import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    asr_url: str = "http://127.0.0.1:8000/v1/audio/transcriptions"
    llm_url: str = "http://127.0.0.1:8000/v1/chat/completions"
    asr_model: str = "VibeVoice-ASR-4bit"
    llm_model: str = "gemma-4-26b-a4b-it-oQ4"
    meetings_dir: Path = Path.home() / "Documents" / "Meetings"
    port: int = 6076

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
