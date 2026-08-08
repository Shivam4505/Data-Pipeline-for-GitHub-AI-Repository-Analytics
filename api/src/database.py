# GitHub AI Repository Analytics - API Database Layer
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
import structlog

from .config import settings

logger = structlog.get_logger(__name__)


class DatabaseManager:
    """Manages database connections for the API."""

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    async def initialize(self) -> None:
        """Initialize database connections."""
        self._engine = create_async_engine(
            settings.postgres_async_dsn,
            pool_size=settings.postgres_pool_size,
            max_overflow=settings.postgres_max_overflow,
            pool_pre_ping=True,
            echo=False,
            poolclass=NullPool,  # Use NullPool for serverless/container environments
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("api_database_initialized")

    async def close(self) -> None:
        """Close database connections."""
        if self._engine:
            await self._engine.dispose()
        logger.info("api_database_closed")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session."""
        if not self._session_factory:
            await self.initialize()
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session."""
    async with db_manager.session() as session:
        yield session