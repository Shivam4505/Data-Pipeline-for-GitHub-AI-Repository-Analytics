# GitHub AI Repository Analytics - Stargazer Models
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class StargazerBase(BaseModel):
    """Base stargazer model."""
    user_id: int
    user_login: str
    starred_at: datetime


class StargazerCreate(StargazerBase):
    """Model for creating a stargazer record."""
    repo_id: int
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class Stargazer(StargazerBase):
    """Full stargazer model with metadata."""
    repo_id: int
    collected_at: datetime
    raw_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class StargazerSummary(BaseModel):
    """Lightweight stargazer summary."""
    user_id: int
    user_login: str
    starred_at: datetime