# GitHub AI Repository Analytics - Pull Request Models
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PullRequestBase(BaseModel):
    """Base pull request model."""
    pr_id: int
    node_id: Optional[str] = None
    number: int
    title: str
    body: Optional[str] = None
    state: str
    draft: bool = False
    author_id: Optional[int] = None
    author_login: Optional[str] = None
    author_type: Optional[str] = None
    assignee_login: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    milestone_title: Optional[str] = None
    base_ref: Optional[str] = None
    base_sha: Optional[str] = None
    head_ref: Optional[str] = None
    head_sha: Optional[str] = None
    head_repo_id: Optional[int] = None
    head_repo_full_name: Optional[str] = None
    comments_count: int = 0
    review_comments_count: int = 0
    commits_count: int = 0
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    mergeable: Optional[bool] = None
    mergeable_state: Optional[str] = None
    merged: bool = False
    merged_at: Optional[datetime] = None
    merged_by_login: Optional[str] = None
    closed_at: Optional[datetime] = None
    is_bot_pr: bool = False
    time_to_merge_hours: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class PullRequestCreate(PullRequestBase):
    """Model for creating a pull request record."""
    repo_id: int
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class PullRequest(PullRequestBase):
    """Full pull request model with metadata."""
    repo_id: int
    collected_at: datetime
    raw_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class PullRequestSummary(BaseModel):
    """Lightweight pull request summary."""
    pr_id: int
    number: int
    title: str
    state: str
    author_login: Optional[str] = None
    merged: bool
    merged_at: Optional[datetime] = None
    additions: int
    deletions: int
    changed_files: int
    created_at: datetime