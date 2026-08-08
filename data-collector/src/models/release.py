# GitHub AI Repository Analytics - Release Models
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class ReleaseBase(BaseModel):
    """Base release model."""
    release_id: int
    node_id: Optional[str] = None
    tag_name: str
    target_commitish: Optional[str] = None
    name: Optional[str] = None
    body: Optional[str] = None
    draft: bool = False
    prerelease: bool = False
    author_id: Optional[int] = None
    author_login: Optional[str] = None
    author_type: Optional[str] = None
    assets: List[Dict[str, Any]] = Field(default_factory=list)
    tarball_url: HttpUrl
    zipball_url: HttpUrl
    html_url: HttpUrl
    created_at: datetime
    published_at: Optional[datetime] = None


class ReleaseCreate(ReleaseBase):
    """Model for creating a release record."""
    repo_id: int
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class Release(ReleaseBase):
    """Full release model with metadata."""
    repo_id: int
    collected_at: datetime
    raw_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class ReleaseSummary(BaseModel):
    """Lightweight release summary."""
    release_id: int
    tag_name: str
    name: Optional[str] = None
    prerelease: bool
    author_login: Optional[str] = None
    published_at: Optional[datetime] = None