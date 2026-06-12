"""Application configuration loaded from environment variables."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration.

    Values are read from environment variables (or a `.env` file in
    development).  Defaults match those used by `docker-compose`.
    """

    database_url: str = (
        "postgresql://mundial_user:mundial_pass_seguro_2026@postgres:5432/mundial_db"
    )
    football_api_token: str = "343be13f1f734c93be81a5a8e2b468db"
    environment: str = "development"
    cors_origins: str = "*"

    football_api_base: str = "https://api.football-data.org/v4"
    football_api_competition: str = "WC"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_list(self) -> list[str]:
        raw = (self.cors_origins or "*").strip()
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
