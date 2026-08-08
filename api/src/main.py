# GitHub AI Repository Analytics - FastAPI Main Application
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
import structlog

from .config import settings
from .database import db_manager
from .cache import cache_manager
from .routers import repositories, analytics
from .models import HealthCheckResponse

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("starting_application")
    await db_manager.initialize()
    await cache_manager.initialize()
    
    # Test database connection
    try:
        async with db_manager.session() as session:
            await session.execute("SELECT 1")
        logger.info("database_connection_ok")
    except Exception as e:
        logger.error("database_connection_failed", error=str(e))
    
    # Test cache connection
    try:
        await cache_manager._client.ping()
        logger.info("cache_connection_ok")
    except Exception as e:
        logger.warning("cache_connection_failed", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("shutting_down_application")
    await db_manager.close()
    await cache_manager.close()


app = FastAPI(
    title="GitHub AI Repository Analytics API",
    description="API for GitHub AI/ML repository analytics and insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(repositories.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


@app.get("/health", response_model=HealthCheckResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    db_status = "unknown"
    cache_status = "unknown"
    
    try:
        async with db_manager.session() as session:
            await session.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    try:
        await cache_manager._client.ping()
        cache_status = "healthy"
    except Exception:
        cache_status = "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" and cache_status == "healthy" else "degraded"
    
    return HealthCheckResponse(
        status=overall_status,
        database=db_status,
        cache=cache_status,
    )


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "name": "GitHub AI Repository Analytics API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )