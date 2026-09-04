"""
Configuration settings for the SanjarBot project.
"""

from typing import List

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings derived from environment variables.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Bot Settings
    bot_token: SecretStr
    admin_ids: List[int]
    webhook_url: str | None = None
    webhook_path: str = "/webhook"
    use_webhook: bool = False

    # Database Settings
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int = 5432

    # Redis Settings
    redis_host: str
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # MinIO Settings
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: SecretStr
    minio_secure: bool = False

    # External APIs
    openai_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None
    weather_api_key: SecretStr | None = None
    currency_api_key: SecretStr | None = None

    # App Settings
    log_level: str = "INFO"
    tz: str = "Asia/Tashkent"

    @computed_field  # type: ignore[misc]
    @property
    def database_url(self) -> str:
        """Construct the async database connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def redis_url(self) -> str:
        """Construct the base Redis connection URL."""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
        
    @computed_field  # type: ignore[misc]
    @property
    def redis_fsm_url(self) -> str:
        """Construct the Redis connection URL for FSM storage."""
        # Typically use a different DB index for FSM, e.g., DB 1
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/1"


settings = Settings()
