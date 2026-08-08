# GitHub AI Repository Analytics - Issue Models
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IssueBase(BaseModel):
    """Base issue model."""
    issue_id: int
    node_id: Optional[str] = None
    number: int
    title: str
    body: Optional[str] = None
    state: str
    state_reason: Optional[str] = None
    author_id: Optional[int] = None
    author_login: Optional[str] = None
    author_type: Optional[str] = None
    assignee_login: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    milestone_title: Optional[str] = None
    milestone_state: Optional[str] = None
    comments_count: int = 0
    reactions_total: int = 0
    is_pull_request: bool = False
    pull_request_url: Optional[str] = None
    is_bot_issue: bool = False
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    resolution_time_hours: Optional[float] = None


class IssueCreate(IssueBase):
    """Model for creating an issue record."""
    repo_id: int
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class Issue(IssueBase):
    """Full issue model with metadata."""
    repo_id: int
    collected_at: datetime
    raw_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class IssueSummary(BaseModel):
    """Lightweight issue summary."""
    issue_id: int
    number: int
    title: str
    state: str
    author_login: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    created_at: datetime
    closed_at: Optional[datetime] = None