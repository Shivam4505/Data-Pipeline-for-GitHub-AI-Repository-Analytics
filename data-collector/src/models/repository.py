# GitHub AI Repository Analytics - Repository Models
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class RepositoryBase(BaseModel):
    """Base repository model."""
    id: int
    node_id: str
    name: str
    full_name: str
    owner_login: str
    owner_type: str
    owner_id: int
    description: Optional[str] = None
    homepage: Optional[HttpUrl] = None
    html_url: HttpUrl
    api_url: HttpUrl
    clone_url: HttpUrl
    ssh_url: HttpUrl
    git_url: HttpUrl
    svn_url: HttpUrl
    language: Optional[str] = None
    languages: Dict[str, int] = Field(default_factory=dict)
    topics: List[str] = Field(default_factory=list)
    default_branch: str
    license_key: Optional[str] = None
    license_name: Optional[str] = None
    license_spdx_id: Optional[str] = None
    license_url: Optional[HttpUrl] = None
    is_private: bool = False
    is_fork: bool = False
    is_archived: bool = False
    is_disabled: bool = False
    is_template: bool = False
    has_issues: bool = True
    has_projects: bool = True
    has_wiki: bool = True
    has_pages: bool = False
    has_downloads: bool = True
    has_discussions: bool = False
    archived_at: Optional[datetime] = None
    pushed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    size_kb: int
    stargazers_count: int = 0
    watchers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    subscribers_count: int = 0
    network_count: int = 0
    contributors_count: int = 0
    releases_count: int = 0
    commits_count: int = 0
    dependencies_count: int = 0
    dependents_count: int = 0
    is_ai_ml_repo: bool = False
    ai_ml_topics: List[str] = Field(default_factory=list)


class RepositoryCreate(RepositoryBase):
    """Model for creating a repository record."""
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class RepositoryUpdate(BaseModel):
    """Model for updating a repository record."""
    description: Optional[str] = None
    homepage: Optional[HttpUrl] = None
    language: Optional[str] = None
    languages: Optional[Dict[str, int]] = None
    topics: Optional[List[str]] = None
    default_branch: Optional[str] = None
    license_key: Optional[str] = None
    license_name: Optional[str] = None
    license_spdx_id: Optional[str] = None
    license_url: Optional[HttpUrl] = None
    is_archived: Optional[bool] = None
    is_disabled: Optional[bool] = None
    pushed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    size_kb: Optional[int] = None
    stargazers_count: Optional[int] = None
    watchers_count: Optional[int] = None
    forks_count: Optional[int] = None
    open_issues_count: Optional[int] = None
    subscribers_count: Optional[int] = None
    network_count: Optional[int] = None
    contributors_count: Optional[int] = None
    releases_count: Optional[int] = None
    commits_count: Optional[int] = None
    is_ai_ml_repo: Optional[bool] = None
    ai_ml_topics: Optional[List[str]] = None


class Repository(RepositoryBase):
    """Full repository model with metadata."""
    collected_at: datetime
    raw_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class RepositorySummary(BaseModel):
    """Lightweight repository summary for lists."""
    id: int
    full_name: str
    description: Optional[str] = None
    language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    stargazers_count: int
    forks_count: int
    open_issues_count: int
    is_ai_ml_repo: bool
    ai_ml_topics: List[str] = Field(default_factory=list)
    pushed_at: Optional[datetime] = None
    created_at: datetime
    health_score: Optional[float] = None
    health_grade: Optional[str] = None