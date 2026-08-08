# GitHub AI Repository Analytics - Analytics API Models
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LanguageTrendDataPoint(BaseModel):
    """Language trend data point."""
    date: date
    language: str
    repo_count: int
    total_stars: int
    total_forks: int
    total_commits: int
    total_contributors: int
    new_repos_count: int


class LanguageTrendsResponse(BaseModel):
    """Language trends response."""
    trends: List[LanguageTrendDataPoint]
    summary: Dict[str, Any] = Field(default_factory=dict)


class TopicTrendDataPoint(BaseModel):
    """Topic trend data point."""
    date: date
    topic: str
    repo_count: int
    total_stars: int
    total_forks: int
    avg_stars_per_repo: float
    new_repos_count: int


class TopicTrendsResponse(BaseModel):
    """Topic trends response."""
    trends: List[TopicTrendDataPoint]
    summary: Dict[str, Any] = Field(default_factory=dict)


class ContributorLeaderboardEntry(BaseModel):
    """Contributor leaderboard entry."""
    rank: int
    contributor_id: int
    login: str
    name: Optional[str] = None
    avatar_url: str
    html_url: str
    company: Optional[str] = None
    location: Optional[str] = None
    total_commits: int
    total_additions: int
    total_deletions: int
    total_prs_merged: int
    total_issues_closed: int
    repos_contributed: int
    period_start: date
    period_end: date
    period_type: str


class ContributorLeaderboardResponse(BaseModel):
    """Contributor leaderboard response."""
    leaderboard: List[ContributorLeaderboardEntry]
    period_start: date
    period_end: date
    period_type: str
    total: int


class SummaryStatsResponse(BaseModel):
    """Dashboard summary statistics."""
    total_repositories: int
    total_ai_ml_repositories: int
    total_contributors: int
    total_commits: int
    total_stars: int
    total_forks: int
    total_issues: int
    total_prs: int
    total_prs_merged: int
    top_languages: List[Dict[str, Any]] = Field(default_factory=list)
    top_topics: List[Dict[str, Any]] = Field(default_factory=list)
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)
    top_repositories: List[Dict[str, Any]] = Field(default_factory=list)
    top_contributors: List[Dict[str, Any]] = Field(default_factory=list)