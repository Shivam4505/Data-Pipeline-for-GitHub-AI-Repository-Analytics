# GitHub AI Repository Analytics - Contributor Models
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class ContributorBase(BaseModel):
    """Base contributor model."""
    contributor_id: int
    contributor_login: str
    contributor_name: Optional[str] = None
    contributor_email: Optional[str] = None
    contributor_company: Optional[str] = None
    contributor_location: Optional[str] = None
    contributor_bio: Optional[str] = None
    contributor_avatar_url: HttpUrl
    contributor_html_url: HttpUrl
    contributor_type: str
    contributor_site_admin: bool = False
    contributions_count: int = 0
    additions: int = 0
    deletions: int = 0
    commit_count: int = 0
    first_contribution_date: Optional[datetime] = None
    last_contribution_date: Optional[datetime] = None
    is_organization_member: bool = False
    is_bot: bool = False


class ContributorCreate(ContributorBase):
    """Model for creating a contributor record."""
    repo_id: int
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class Contributor(ContributorBase):
    """Full contributor model with metadata."""
    repo_id: int
    collected_at: datetime
    raw_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class ContributorSummary(BaseModel):
    """Lightweight contributor summary."""
    contributor_id: int
    contributor_login: str
    contributor_name: Optional[str] = None
    contributor_avatar_url: HttpUrl
    contributor_html_url: HttpUrl
    contributions_count: int
    commit_count: int
    is_bot: bool