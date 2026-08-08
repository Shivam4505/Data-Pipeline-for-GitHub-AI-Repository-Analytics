# GitHub AI Repository Analytics - Commit Models
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CommitBase(BaseModel):
    """Base commit model."""
    sha: str
    node_id: Optional[str] = None
    author_id: Optional[int] = None
    author_login: Optional[str] = None
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    author_date: datetime
    committer_id: Optional[int] = None
    committer_login: Optional[str] = None
    committer_name: Optional[str] = None
    committer_email: Optional[str] = None
    committer_date: datetime
    message: str
    message_headline: Optional[str] = None
    additions: int = 0
    deletions: int = 0
    total_changes: int = 0
    files_changed: int = 0
    parents_sha: List[str] = Field(default_factory=list)
    is_merge: bool = False
    is_bot_commit: bool = False


class CommitCreate(CommitBase):
    """Model for creating a commit record."""
    repo_id: int
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class Commit(CommitBase):
    """Full commit model with metadata."""
    repo_id: int
    collected_at: datetime
    raw_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class CommitSummary(BaseModel):
    """Lightweight commit summary."""
    sha: str
    author_login: Optional[str] = None
    author_date: datetime
    message_headline: Optional[str] = None
    additions: int
    deletions: int
    files_changed: int