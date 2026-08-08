# GitHub AI Repository Analytics - Commit Collector
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
import structlog

from ..config import settings
from ..github_client import GitHubClient
from ..logging_config import get_logger
from ..models import CommitCreate

logger = get_logger(__name__)


class CommitCollector:
    """Collects commit data from GitHub repositories."""

    def __init__(self, client: GitHubClient):
        self.client = client
        self.stats = {
            "total_collected": 0,
            "total_repos": 0,
            "errors": 0,
        }

    def _parse_commit(
        self,
        repo_id: int,
        commit_data: Dict[str, Any],
    ) -> CommitCreate:
        """Parse GitHub commit data into our model."""
        commit = commit_data.get("commit", {})
        author = commit.get("author", {})
        committer = commit.get("committer", {})
        author_info = commit_data.get("author") or {}
        committer_info = commit_data.get("committer") or {}

        return CommitCreate(
            repo_id=repo_id,
            sha=commit_data["sha"],
            node_id=commit_data.get("node_id"),
            author_id=author_info.get("id"),
            author_login=author_info.get("login"),
            author_name=author.get("name"),
            author_email=author.get("email"),
            author_date=self._parse_datetime(author.get("date")),
            committer_id=committer_info.get("id"),
            committer_login=committer_info.get("login"),
            committer_name=committer.get("name"),
            committer_email=committer.get("email"),
            committer_date=self._parse_datetime(committer.get("date")),
            message=commit.get("message", ""),
            message_headline=commit.get("message", "").split("\n")[0][:500],
            additions=commit_data.get("stats", {}).get("additions", 0),
            deletions=commit_data.get("stats", {}).get("deletions", 0),
            total_changes=commit_data.get("stats", {}).get("total", 0),
            files_changed=len(commit_data.get("files", [])),
            parents_sha=[p["sha"] for p in commit_data.get("parents", [])],
            is_merge=len(commit_data.get("parents", [])) > 1,
            is_bot_commit=(
                (author_info.get("login", "").lower().endswith("[bot]") if author_info else False) or
                "bot" in (author.get("email", "").lower() if author else "")
            ),
            raw_data=commit_data,
        )

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except Exception:
            return None

    async def collect_for_repository(
        self,
        repo_id: int,
        owner: str,
        repo: str,
        since: Optional[str] = None,
        until: Optional[str] = None,
        max_commits: Optional[int] = None,
    ) -> List[CommitCreate]:
        """Collect commits for a single repository."""
        max_commits = max_commits or settings.max_commits_per_repo
        commits = []

        try:
            count = 0
            async for commit in self.client.get_commits(
                owner, repo, since=since, until=until, max_results=max_commits
            ):
                # Get detailed commit info for stats
                try:
                    detailed = await self.client.get_commit(owner, repo, commit["sha"])
                    parsed = self._parse_commit(repo_id, detailed)
                except Exception:
                    # Fallback to basic info
                    parsed = self._parse_commit(repo_id, commit)
                
                commits.append(parsed)
                count += 1

            self.stats["total_collected"] += count
            self.stats["total_repos"] += 1
            logger.info("commits_collected", repo=f"{owner}/{repo}", count=count)

        except Exception as e:
            logger.error("collect_commits_failed", repo=f"{owner}/{repo}", error=str(e))
            self.stats["errors"] += 1

        return commits

    async def collect_for_repositories(
        self,
        repositories: List[Dict[str, Any]],
        since: Optional[str] = None,
        until: Optional[str] = None,
        max_commits: Optional[int] = None,
    ) -> Dict[int, List[CommitCreate]]:
        """Collect commits for multiple repositories."""
        results = {}

        for repo in repositories:
            repo_id = repo["id"]
            owner = repo["owner_login"]
            name = repo["name"]

            commits = await self.collect_for_repository(
                repo_id, owner, name, since, until, max_commits
            )
            results[repo_id] = commits

            # Rate limiting between repos
            await asyncio.sleep(settings.collection_rate_limit_delay)

        return results

    def get_stats(self) -> Dict[str, int]:
        """Get collection statistics."""
        return self.stats.copy()


async def collect_commits(
    client: GitHubClient,
    repositories: List[Dict[str, Any]],
    since: Optional[str] = None,
    until: Optional[str] = None,
    max_commits: Optional[int] = None,
) -> Dict[int, List[CommitCreate]]:
    """Convenience function to collect commits."""
    collector = CommitCollector(client)
    return await collector.collect_for_repositories(repositories, since, until, max_commits)