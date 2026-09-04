"""
Configuration settings for the SanjarBot project.
Supports all spec environment variables, aliases, and defaults.
"""

from typing import List, Optional
from pydantic import SecretStr, computed_field, Field, field_validator
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
    admin_ids: List[int] = Field(default_factory=lambda: [7537966029])
    bot_admin_ids: List[int] = Field(default_factory=lambda: [7537966029])

    @field_validator("admin_ids", "bot_admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                import json
                return json.loads(v)
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v
    webhook_url: Optional[str] = None
    bot_webhook_url: str = ""
    webhook_path: str = "/webhook"
    bot_webhook_secret: str = ""
    use_webhook: bool = False
    bot_mode: str = "polling"

    # Database Settings
    postgres_user: str = "sanjar"
    postgres_password: str = "secret"
    postgres_db: str = "sanjar_bot_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "sanjar"
    db_password: Optional[SecretStr] = None
    db_name: str = "sanjar_bot_db"
    db_echo: bool = False
    db_pool_size: int = 20
    db_max_overflow: int = 10

    # Redis Settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_fsm_db: int = 1
    redis_cache_db: int = 2
    redis_max_connections: int = 50

    # MinIO Settings
    minio_host: str = "localhost"
    minio_port: int = 9000
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: SecretStr = SecretStr("minioadmin")
    minio_bucket: str = "sanjar-bot-files"
    minio_secure: bool = False

    # External APIs
    openai_api_key: Optional[SecretStr] = None
    gemini_api_key: Optional[SecretStr] = None
    weather_api_key: Optional[SecretStr] = None
    openweather_api_key: Optional[SecretStr] = None
    currency_api_key: Optional[SecretStr] = None
    exchange_rate_api_key: Optional[SecretStr] = None
    ai_default_provider: str = "gemini"
    ai_max_tokens: int = 4096
    ai_temperature: float = 0.7

    # App Settings
    encryption_key: SecretStr = SecretStr("gB4npx0bWoHdwQ6bJl7nNdT532wIN7or_tXBA9F_o08=")
    rate_limit_requests: int = 30
    rate_limit_period: int = 60
    log_level: str = "INFO"
    log_format: str = "json"
    tz: str = "Asia/Tashkent"
    default_locale: str = "uz"
    supported_locales: List[str] = Field(default_factory=lambda: ["uz", "en", "ru"])

    @computed_field  # type: ignore[misc]
    @property
    def database_url(self) -> str:
        """Construct the async database connection URL."""
        user = self.postgres_user or self.db_user
        pwd = (self.db_password.get_secret_value() if self.db_password else self.postgres_password)
        host = self.postgres_host or self.db_host
        port = self.postgres_port or self.db_port
        db = self.postgres_db or self.db_name
        return f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}"

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
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_fsm_db}"

    def __getattr__(self, name: str):
        lower_name = name.lower()
        try:
            return super().__getattribute__(lower_name)
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


settings = Settings()
