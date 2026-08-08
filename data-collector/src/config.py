# GitHub AI Repository Analytics - Configuration
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

    # GitHub API
    github_token: str = Field(..., description="GitHub Personal Access Token")
    github_api_base_url: str = "https://api.github.com"
    github_graphql_url: str = "https://api.github.com/graphql"
    github_rate_limit_buffer: int = 100  # Keep this many requests in reserve

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "github_analytics"
    postgres_user: str = "analytics"
    postgres_password: str = "secure_password"
    postgres_pool_size: int = 10
    postgres_max_overflow: int = 20

    # MinIO / S3
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket_raw: str = "raw-data"
    minio_bucket_processed: str = "processed-data"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # Collection Settings
    collection_batch_size: int = 100
    collection_rate_limit_delay: float = 1.0
    max_repositories_per_run: int = 500
    max_commits_per_repo: int = 1000
    max_issues_per_repo: int = 500
    max_prs_per_repo: int = 500
    max_contributors_per_repo: int = 200

    # Search Queries for AI/ML repos
    github_search_queries: List[str] = Field(
        default=[
            "topic:machine-learning stars:>1000",
            "topic:deep-learning stars:>1000",
            "topic:artificial-intelligence stars:>1000",
            "topic:nlp stars:>500",
            "topic:computer-vision stars:>500",
            "topic:reinforcement-learning stars:>500",
            "topic:llm stars:>500",
            "topic:transformers stars:>500",
            "language:python topic:ai stars:>1000",
            "language:python topic:ml stars:>1000",
            "topic:tensorflow stars:>500",
            "topic:pytorch stars:>500",
            "topic:huggingface stars:>500",
            "topic:langchain stars:>500",
            "topic:openai stars:>500",
        ],
        description="GitHub search queries to find AI/ML repositories"
    )

    # AI/ML Topics for classification
    ai_ml_topics: List[str] = Field(
        default=[
            "machine-learning", "deep-learning", "artificial-intelligence",
            "nlp", "computer-vision", "reinforcement-learning",
            "llm", "transformers", "ai", "ml", "data-science",
            "neural-network", "tensorflow", "pytorch", "keras",
            "scikit-learn", "huggingface", "openai", "langchain",
            "llama", "gpt", "bert", "diffusion", "gan", "rl"
        ],
        description="Topics that classify a repo as AI/ML"
    )

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Scheduling
    collection_schedule_cron: str = "0 2 * * *"  # Daily at 2 AM UTC
    health_check_schedule_cron: str = "0 */6 * * *"  # Every 6 hours

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