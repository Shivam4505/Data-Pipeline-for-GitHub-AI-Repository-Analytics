# GitHub AI Repository Analytics - Contributor Collector
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
import structlog

from ..config import settings
from ..github_client import GitHubClient
from ..logging_config import get_logger
from ..models import ContributorCreate

logger = get_logger(__name__)


class ContributorCollector:
    """Collects contributor data from GitHub repositories."""

    def __init__(self, client: GitHubClient):
        self.client = client
        self.stats = {
            "total_collected": 0,
            "total_repos": 0,
            "errors": 0,
        }

    def _parse_contributor(
        self,
        repo_id: int,
        contrib_data: Dict[str, Any],
    ) -> ContributorCreate:
        """Parse GitHub contributor data into our model."""
        return ContributorCreate(
            repo_id=repo_id,
            contributor_id=contrib_data["id"],
            contributor_login=contrib_data["login"],
            contributor_name=contrib_data.get("name"),
            contributor_email=contrib_data.get("email"),
            contributor_company=contrib_data.get("company"),
            contributor_location=contrib_data.get("location"),
            contributor_bio=contrib_data.get("bio"),
            contributor_avatar_url=contrib_data["avatar_url"],
            contributor_html_url=contrib_data["html_url"],
            contributor_type=contrib_data.get("type", "User"),
            contributor_site_admin=contrib_data.get("site_admin", False),
            contributions_count=contrib_data.get("contributions", 0),
            additions=0,  # Would need commit details
            deletions=0,
            commit_count=0,
            first_contribution_date=None,
            last_contribution_date=None,
            is_organization_member=False,
            is_bot=contrib_data["login"].lower().endswith("[bot]") or "bot" in contrib_data["login"].lower(),
            raw_data=contrib_data,
        )

    async def collect_for_repository(
        self,
        repo_id: int,
        owner: str,
        repo: str,
        max_contributors: Optional[int] = None,
    ) -> List[ContributorCreate]:
        """Collect contributors for a single repository."""
        max_contributors = max_contributors or settings.max_contributors_per_repo
        contributors = []

        try:
            count = 0
            async for contrib in self.client.get_contributors(
                owner, repo, max_results=max_contributors
            ):
                parsed = self._parse_contributor(repo_id, contrib)
                contributors.append(parsed)
                count += 1

            self.stats["total_collected"] += count
            self.stats["total_repos"] += 1
            logger.info("contributors_collected", repo=f"{owner}/{repo}", count=count)

        except Exception as e:
            logger.error("collect_contributors_failed", repo=f"{owner}/{repo}", error=str(e))
            self.stats["errors"] += 1

        return contributors

    async def collect_for_repositories(
        self,
        repositories: List[Dict[str, Any]],
        max_contributors: Optional[int] = None,
    ) -> Dict[int, List[ContributorCreate]]:
        """Collect contributors for multiple repositories."""
        results = {}

        for repo in repositories:
            repo_id = repo["id"]
            owner = repo["owner_login"]
            name = repo["name"]

            contributors = await self.collect_for_repository(
                repo_id, owner, name, max_contributors
            )
            results[repo_id] = contributors

            # Rate limiting between repos
            await asyncio.sleep(settings.collection_rate_limit_delay)

        return results

    def get_stats(self) -> Dict[str, int]:
        """Get collection statistics."""
        return self.stats.copy()


async def collect_contributors(
    client: GitHubClient,
    repositories: List[Dict[str, Any]],
    max_contributors: Optional[int] = None,
) -> Dict[int, List[ContributorCreate]]:
    """Convenience function to collect contributors."""
    collector = ContributorCollector(client)
    return await collector.collect_for_repositories(repositories, max_contributors)