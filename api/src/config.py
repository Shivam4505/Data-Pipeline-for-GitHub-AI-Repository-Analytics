# GitHub AI Repository Analytics - API Configuration
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "github_analytics"
    postgres_user: str = "analytics"
    postgres_password: str = "secure_password"
    postgres_pool_size: int = 10
    postgres_max_overflow: int = 20

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = Field(default=["http://localhost:3000"])

    # Cache
    cache_ttl_seconds: int = 300  # 5 minutes
    cache_enabled: bool = True

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def postgres_async_dsn(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()