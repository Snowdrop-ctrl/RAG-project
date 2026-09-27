from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    cors_origins: str = "http://localhost:5173"

    # DeepSeek (OpenAI-compatible chat completions API)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    llm_timeout_seconds: float = 90.0
    llm_max_tokens: int = 1024

    # Retrieval
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chroma_dir: str = str(BACKEND_DIR / "data" / "chroma")
    docs_dir: str = str(BACKEND_DIR / "data" / "docs")
    chunk_words: int = 200
    chunk_overlap_words: int = 40
    top_k: int = 4
    min_score: float = 0.25

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
