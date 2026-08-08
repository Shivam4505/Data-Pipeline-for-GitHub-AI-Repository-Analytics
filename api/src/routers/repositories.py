# GitHub AI Repository Analytics - Repository Router
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..cache import get_cache, CacheManager
from ..models import (
    RepositoryListResponse,
    RepositoryResponse,
    RepositoryDetailResponse,
    RepositoryActivityResponse,
    RepositoryContributorsResponse,
    RepositoryHealthResponse,
    PaginationParams,
    DateRangeParams,
)
from ..config import settings

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.get("", response_model=RepositoryListResponse)
async def list_repositories(
    pagination: PaginationParams = Depends(),
    language: Optional[str] = Query(None, description="Filter by primary language"),
    is_ai_ml: Optional[bool] = Query(None, description="Filter AI/ML repositories"),
    min_stars: Optional[int] = Query(None, ge=0, description="Minimum stars"),
    max_stars: Optional[int] = Query(None, ge=0, description="Maximum stars"),
    sort_by: str = Query("stargazers_count", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    search: Optional[str] = Query(None, description="Search in name/description"),
    db: AsyncSession = Depends(get_db_session),
    cache: CacheManager = Depends(get_cache),
):
    """List repositories with filtering and pagination."""
    cache_key = cache.make_key(
        "repos_list",
        f"p{pagination.page}_pp{pagination.per_page}",
        f"lang_{language or 'all'}",
        f"ai_{is_ai_ml or 'all'}",
        f"stars_{min_stars or 0}_{max_stars or 'inf'}",
        f"sort_{sort_by}_{sort_order}",
        f"search_{search or 'none'}",
    )

    cached = await cache.get(cache_key)
    if cached:
        return cached

    # Build query
    query = select(
        func.count()
    ).select_from(
        # We'll use a subquery for the count
    )

    # For now, return mock data structure
    # In production, this would query the marts.dim_repository table
    items = []
    total = 0

    response = RepositoryListResponse(
        items=items,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=0,
    )

    await cache.set(cache_key, response.model_dump())
    return response


@router.get("/{repo_id}", response_model=RepositoryDetailResponse)
async def get_repository(
    repo_id: int,
    db: AsyncSession = Depends(get_db_session),
    cache: CacheManager = Depends(get_cache),
):
    """Get detailed repository information."""
    cache_key = cache.make_key("repo_detail", str(repo_id))
    cached = await cache.get(cache_key)
    if cached:
        return cached

    # Query would go here
    raise HTTPException(status_code=404, detail="Repository not found")


@router.get("/{repo_id}/activity", response_model=RepositoryActivityResponse)
async def get_repository_activity(
    repo_id: int,
    date_range: DateRangeParams = Depends(),
    db: AsyncSession = Depends(get_db_session),
    cache: CacheManager = Depends(get_cache),
):
    """Get repository activity timeline."""
    cache_key = cache.make_key(
        "repo_activity",
        str(repo_id),
        f"start_{date_range.start_date or 'none'}",
        f"end_{date_range.end_date or 'none'}",
    )
    cached = await cache.get(cache_key)
    if cached:
        return cached

    # Query would go here
    raise HTTPException(status_code=404, detail="Repository not found")


@router.get("/{repo_id}/contributors", response_model=RepositoryContributorsResponse)
async def get_repository_contributors(
    repo_id: int,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db_session),
    cache: CacheManager = Depends(get_cache),
):
    """Get top contributors for a repository."""
    cache_key = cache.make_key(
        "repo_contributors",
        str(repo_id),
        f"p{pagination.page}_pp{pagination.per_page}",
    )
    cached = await cache.get(cache_key)
    if cached:
        return cached

    # Query would go here
    raise HTTPException(status_code=404, detail="Repository not found")


@router.get("/{repo_id}/health", response_model=RepositoryHealthResponse)
async def get_repository_health(
    repo_id: int,
    db: AsyncSession = Depends(get_db_session),
    cache: CacheManager = Depends(get_cache),
):
    """Get repository health metrics."""
    cache_key = cache.make_key("repo_health", str(repo_id))
    cached = await cache.get(cache_key)
    if cached:
        return cached

    # Query would go here
    raise HTTPException(status_code=404, detail="Repository not found")