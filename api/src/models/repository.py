# GitHub AI Repository Analytics - Repository API Models
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class RepositoryBase(BaseModel):
    """Base repository model."""
    repo_id: int
    full_name: str
    name: str
    owner_login: str
    owner_type: str
    description: Optional[str] = None
    homepage: Optional[HttpUrl] = None
    html_url: HttpUrl
    primary_language: Optional[str] = None
    languages: Dict[str, int] = Field(default_factory=dict)
    topics: List[str] = Field(default_factory=list)
    ai_ml_topics: List[str] = Field(default_factory=list)
    is_ai_ml_repo: bool = False
    license_key: Optional[str] = None
    license_name: Optional[str] = None
    is_fork: bool = False
    is_archived: bool = False
    default_branch: str
    created_at: datetime
    updated_at: datetime
    pushed_at: Optional[datetime] = None
    size_kb: int
    stargazers_count: int
    watchers_count: int
    forks_count: int
    open_issues_count: int
    subscribers_count: int
    network_count: int
    contributors_count: int
    releases_count: int
    commits_count: int


class RepositoryResponse(RepositoryBase):
    """Repository response for lists."""
    health_score: Optional[float] = None
    health_grade: Optional[str] = None
    maturity_level: Optional[str] = None


class RepositoryListResponse(BaseModel):
    """Paginated repository list response."""
    items: List[RepositoryResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class RepositoryDetailResponse(RepositoryBase):
    """Detailed repository response."""
    health_score: Optional[float] = None
    health_grade: Optional[str] = None
    maturity_level: Optional[str] = None
    # Health metrics
    avg_commits_per_week: Optional[float] = None
    avg_prs_per_week: Optional[float] = None
    avg_issues_per_week: Optional[float] = None
    active_contributors_30d: Optional[int] = None
    active_contributors_90d: Optional[int] = None
    pr_merge_rate: Optional[float] = None
    avg_pr_merge_time_hours: Optional[float] = None
    issue_resolution_rate: Optional[float] = None
    avg_issue_resolution_time_hours: Optional[float] = None
    bus_factor: Optional[int] = None
    core_contributors_count: Optional[int] = None
    external_contributors_ratio: Optional[float] = None
    release_frequency_days: Optional[float] = None
    last_release_date: Optional[datetime] = None
    releases_last_year: Optional[int] = None
    stars_growth_rate_30d: Optional[float] = None
    forks_growth_rate_30d: Optional[float] = None
    contributors_growth_rate_30d: Optional[float] = None


class ActivityDataPoint(BaseModel):
    """Single activity data point."""
    date: date
    commits_count: int
    additions: int
    deletions: int
    files_changed: int
    unique_contributors: int
    issues_opened: int
    issues_closed: int
    prs_opened: int
    prs_closed: int
    prs_merged: int
    releases_published: int
    stars_gained: int
    forks_gained: int
    watchers_gained: int


class RepositoryActivityResponse(BaseModel):
    """Repository activity timeline response."""
    repo_id: int
    full_name: str
    activity: List[ActivityDataPoint]
    summary: Dict[str, Any] = Field(default_factory=dict)


class ContributorSummary(BaseModel):
    """Contributor summary for repository."""
    contributor_id: int
    login: str
    name: Optional[str] = None
    avatar_url: HttpUrl
    html_url: HttpUrl
    contributions_count: int
    commit_count: int
    is_bot: bool


class RepositoryContributorsResponse(BaseModel):
    """Repository contributors response."""
    repo_id: int
    full_name: str
    contributors: List[ContributorSummary]
    total: int


class RepositoryHealthResponse(BaseModel):
    """Repository health metrics response."""
    repo_id: int
    full_name: str
    health_score: float
    health_grade: str
    metrics: Dict[str, Any]
    recommendations: List[str] = Field(default_factory=list)