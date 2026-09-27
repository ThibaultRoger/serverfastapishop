from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "apiservershoptest2"
    app_version: str = "dev"      # APP_VERSION, fixé par le pipeline (branche ou tag)
    git_sha: str = "unknown"       # GIT_SHA, commit de l'image
    app_description: str = "API Server shop."
    database_url: str = "postgresql+psycopg://localhost/apiservershoptest2"
    db_pool_size: int = 5
    db_echo: bool = False

    @field_validator("database_url")
    @classmethod
    def _use_psycopg3(cls, url: str) -> str:
        """Accepte postgresql://… ou postgres://… (forme usuelle) : le pilote installé est psycopg 3."""
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url[len(prefix):]
        return url


settings = Settings()
