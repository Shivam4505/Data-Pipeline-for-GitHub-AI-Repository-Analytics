# GitHub AI Repository Analytics - Issue & PR Collector
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
import structlog

from ..config import settings
from ..github_client import GitHubClient
from ..logging_config import get_logger
from ..models import IssueCreate, PullRequestCreate

logger = get_logger(__name__)


class IssuePRCollector:
    """Collects issues and pull requests from GitHub repositories."""

    def __init__(self, client: GitHubClient):
        self.client = client
        self.stats = {
            "issues_collected": 0,
            "prs_collected": 0,
            "total_repos": 0,
            "errors": 0,
        }

    def _parse_issue(
        self,
        repo_id: int,
        issue_data: Dict[str, Any],
    ) -> IssueCreate:
        """Parse GitHub issue data into our model."""
        user = issue_data.get("user", {})
        assignee = issue_data.get("assignee")
        labels = [label["name"] for label in issue_data.get("labels", [])]
        milestone = issue_data.get("milestone")
        reactions = issue_data.get("reactions", {})

        return IssueCreate(
            repo_id=repo_id,
            issue_id=issue_data["id"],
            node_id=issue_data.get("node_id"),
            number=issue_data["number"],
            title=issue_data["title"],
            body=issue_data.get("body"),
            state=issue_data["state"],
            state_reason=issue_data.get("state_reason"),
            author_id=user.get("id"),
            author_login=user.get("login"),
            author_type=user.get("type"),
            assignee_login=assignee.get("login") if assignee else None,
            labels=labels,
            milestone_title=milestone.get("title") if milestone else None,
            milestone_state=milestone.get("state") if milestone else None,
            comments_count=issue_data.get("comments", 0),
            reactions_total=reactions.get("total_count", 0),
            is_pull_request="pull_request" in issue_data,
            pull_request_url=issue_data.get("pull_request", {}).get("url") if "pull_request" in issue_data else None,
            is_bot_issue=user.get("login", "").lower().endswith("[bot]") or "bot" in user.get("login", "").lower(),
            created_at=self._parse_datetime(issue_data["created_at"]),
            updated_at=self._parse_datetime(issue_data["updated_at"]),
            closed_at=self._parse_datetime(issue_data.get("closed_at")),
            resolution_time_hours=None,  # Calculated in DB
            raw_data=issue_data,
        )

    def _parse_pull_request(
        self,
        repo_id: int,
        pr_data: Dict[str, Any],
    ) -> PullRequestCreate:
        """Parse GitHub PR data into our model."""
        user = pr_data.get("user", {})
        assignee = pr_data.get("assignee")
        labels = [label["name"] for label in pr_data.get("labels", [])]
        milestone = pr_data.get("milestone")
        head = pr_data.get("head", {})
        base = pr_data.get("base", {})
        head_repo = head.get("repo", {})

        return PullRequestCreate(
            repo_id=repo_id,
            pr_id=pr_data["id"],
            node_id=pr_data.get("node_id"),
            number=pr_data["number"],
            title=pr_data["title"],
            body=pr_data.get("body"),
            state=pr_data["state"],
            draft=pr_data.get("draft", False),
            author_id=user.get("id"),
            author_login=user.get("login"),
            author_type=user.get("type"),
            assignee_login=assignee.get("login") if assignee else None,
            labels=labels,
            milestone_title=milestone.get("title") if milestone else None,
            base_ref=base.get("ref"),
            base_sha=base.get("sha"),
            head_ref=head.get("ref"),
            head_sha=head.get("sha"),
            head_repo_id=head_repo.get("id"),
            head_repo_full_name=head_repo.get("full_name"),
            comments_count=pr_data.get("comments", 0),
            review_comments_count=pr_data.get("review_comments", 0),
            commits_count=pr_data.get("commits", 0),
            additions=pr_data.get("additions", 0),
            deletions=pr_data.get("deletions", 0),
            changed_files=pr_data.get("changed_files", 0),
            mergeable=pr_data.get("mergeable"),
            mergeable_state=pr_data.get("mergeable_state"),
            merged=pr_data.get("merged", False),
            merged_at=self._parse_datetime(pr_data.get("merged_at")),
            merged_by_login=pr_data.get("merged_by", {}).get("login") if pr_data.get("merged_by") else None,
            closed_at=self._parse_datetime(pr_data.get("closed_at")),
            is_bot_pr=user.get("login", "").lower().endswith("[bot]") or "bot" in user.get("login", "").lower(),
            time_to_merge_hours=None,  # Calculated in DB
            created_at=self._parse_datetime(pr_data["created_at"]),
            updated_at=self._parse_datetime(pr_data["updated_at"]),
            raw_data=pr_data,
        )

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except Exception:
            return None

    async def collect_issues_for_repository(
        self,
        repo_id: int,
        owner: str,
        repo: str,
        state: str = "all",
        since: Optional[str] = None,
        max_issues: Optional[int] = None,
    ) -> List[IssueCreate]:
        """Collect issues for a single repository."""
        max_issues = max_issues or settings.max_issues_per_repo
        issues = []

        try:
            count = 0
            async for issue in self.client.get_issues(
                owner, repo, state=state, since=since, max_results=max_issues
            ):
                # Skip pull requests (they're collected separately)
                if "pull_request" in issue:
                    continue
                
                parsed = self._parse_issue(repo_id, issue)
                issues.append(parsed)
                count += 1

            self.stats["issues_collected"] += count
            logger.info("issues_collected", repo=f"{owner}/{repo}", count=count)

        except Exception as e:
            logger.error("collect_issues_failed", repo=f"{owner}/{repo}", error=str(e))
            self.stats["errors"] += 1

        return issues

    async def collect_prs_for_repository(
        self,
        repo_id: int,
        owner: str,
        repo: str,
        state: str = "all",
        max_prs: Optional[int] = None,
    ) -> List[PullRequestCreate]:
        """Collect pull requests for a single repository."""
        max_prs = max_prs or settings.max_prs_per_repo
        prs = []

        try:
            count = 0
            async for pr in self.client.get_pull_requests(
                owner, repo, state=state, max_results=max_prs
            ):
                parsed = self._parse_pull_request(repo_id, pr)
                prs.append(parsed)
                count += 1

            self.stats["prs_collected"] += count
            logger.info("prs_collected", repo=f"{owner}/{repo}", count=count)

        except Exception as e:
            logger.error("collect_prs_failed", repo=f"{owner}/{repo}", error=str(e))
            self.stats["errors"] += 1

        return prs

    async def collect_for_repository(
        self,
        repo_id: int,
        owner: str,
        repo: str,
        since: Optional[str] = None,
        max_issues: Optional[int] = None,
        max_prs: Optional[int] = None,
    ) -> tuple[List[IssueCreate], List[PullRequestCreate]]:
        """Collect both issues and PRs for a repository."""
        issues = await self.collect_issues_for_repository(
            repo_id, owner, repo, since=since, max_issues=max_issues
        )
        prs = await self.collect_prs_for_repository(
            repo_id, owner, repo, max_prs=max_prs
        )
        self.stats["total_repos"] += 1
        return issues, prs

    async def collect_for_repositories(
        self,
        repositories: List[Dict[str, Any]],
        since: Optional[str] = None,
        max_issues: Optional[int] = None,
        max_prs: Optional[int] = None,
    ) -> Dict[int, tuple[List[IssueCreate], List[PullRequestCreate]]]:
        """Collect issues and PRs for multiple repositories."""
        results = {}

        for repo in repositories:
            repo_id = repo["id"]
            owner = repo["owner_login"]
            name = repo["name"]

            issues, prs = await self.collect_for_repository(
                repo_id, owner, name, since, max_issues, max_prs
            )
            results[repo_id] = (issues, prs)

            # Rate limiting between repos
            await asyncio.sleep(settings.collection_rate_limit_delay)

        return results

    def get_stats(self) -> Dict[str, int]:
        """Get collection statistics."""
        return self.stats.copy()


async def collect_issues_and_prs(
    client: GitHubClient,
    repositories: List[Dict[str, Any]],
    since: Optional[str] = None,
    max_issues: Optional[int] = None,
    max_prs: Optional[int] = None,
) -> Dict[int, tuple[List[IssueCreate], List[PullRequestCreate]]]:
    """Convenience function to collect issues and PRs."""
    collector = IssuePRCollector(client)
    return await collector.collect_for_repositories(repositories, since, max_issues, max_prs)