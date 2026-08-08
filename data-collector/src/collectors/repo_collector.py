# GitHub AI Repository Analytics - Repository Collector
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
import structlog

from ..config import settings
from ..github_client import GitHubClient, create_github_client
from ..logging_config import get_logger
from ..models import RepositoryCreate

logger = get_logger(__name__)


class RepositoryCollector:
    """Collects repository metadata from GitHub."""

    def __init__(self, client: Optional[GitHubClient] = None):
        self.client = client
        self._own_client = client is None
        self.collected_repos: Set[int] = set()
        self.stats = {
            "total_found": 0,
            "total_collected": 0,
            "total_updated": 0,
            "errors": 0,
        }

    async def __aenter__(self) -> "RepositoryCollector":
        if self._own_client:
            self.client = await create_github_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._own_client and self.client:
            await self.client.close()

    def _parse_repository(self, repo_data: Dict[str, Any]) -> RepositoryCreate:
        """Parse GitHub repository data into our model."""
        owner = repo_data.get("owner", {})
        license_info = repo_data.get("license") or {}
        
        # Get languages (will be fetched separately)
        languages = repo_data.get("languages", {})
        
        # Get topics
        topics = repo_data.get("topics", [])
        
        # Determine if AI/ML repo
        ai_ml_topics = [t for t in topics if t.lower() in settings.ai_ml_topics]
        is_ai_ml = len(ai_ml_topics) > 0

        return RepositoryCreate(
            id=repo_data["id"],
            node_id=repo_data["node_id"],
            name=repo_data["name"],
            full_name=repo_data["full_name"],
            owner_login=owner.get("login", ""),
            owner_type=owner.get("type", "User"),
            owner_id=owner.get("id", 0),
            description=repo_data.get("description"),
            homepage=repo_data.get("homepage"),
            html_url=repo_data["html_url"],
            api_url=repo_data["url"],
            clone_url=repo_data["clone_url"],
            ssh_url=repo_data["ssh_url"],
            git_url=repo_data["git_url"],
            svn_url=repo_data["svn_url"],
            language=repo_data.get("language"),
            languages=languages,
            topics=topics,
            default_branch=repo_data.get("default_branch", "main"),
            license_key=license_info.get("key"),
            license_name=license_info.get("name"),
            license_spdx_id=license_info.get("spdx_id"),
            license_url=license_info.get("url"),
            is_private=repo_data.get("private", False),
            is_fork=repo_data.get("fork", False),
            is_archived=repo_data.get("archived", False),
            is_disabled=repo_data.get("disabled", False),
            is_template=repo_data.get("is_template", False),
            has_issues=repo_data.get("has_issues", True),
            has_projects=repo_data.get("has_projects", True),
            has_wiki=repo_data.get("has_wiki", True),
            has_pages=repo_data.get("has_pages", False),
            has_downloads=repo_data.get("has_downloads", True),
            has_discussions=repo_data.get("has_discussions", False),
            archived_at=self._parse_datetime(repo_data.get("archived_at")),
            pushed_at=self._parse_datetime(repo_data.get("pushed_at")),
            created_at=self._parse_datetime(repo_data["created_at"]),
            updated_at=self._parse_datetime(repo_data["updated_at"]),
            size_kb=repo_data.get("size", 0),
            stargazers_count=repo_data.get("stargazers_count", 0),
            watchers_count=repo_data.get("watchers_count", 0),
            forks_count=repo_data.get("forks_count", 0),
            open_issues_count=repo_data.get("open_issues_count", 0),
            subscribers_count=repo_data.get("subscribers_count", 0),
            network_count=repo_data.get("network_count", 0),
            contributors_count=0,  # Will be updated later
            releases_count=0,  # Will be updated later
            commits_count=0,  # Will be updated later
            is_ai_ml_repo=is_ai_ml,
            ai_ml_topics=ai_ml_topics,
            raw_data=repo_data,
        )

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except Exception:
            return None

    async def collect_from_search(
        self,
        queries: Optional[List[str]] = None,
        max_per_query: Optional[int] = None,
    ) -> List[RepositoryCreate]:
        """Collect repositories using search queries."""
        if not self.client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        queries = queries or settings.github_search_queries
        max_per_query = max_per_query or settings.max_repositories_per_run
        all_repos = []

        for query in queries:
            logger.info("searching_repositories", query=query)
            try:
                count = 0
                async for repo in self.client.search_repositories(
                    query=query,
                    max_results=max_per_query,
                ):
                    if repo["id"] in self.collected_repos:
                        continue
                    
                    self.collected_repos.add(repo["id"])
                    parsed = self._parse_repository(repo)
                    all_repos.append(parsed)
                    count += 1
                    self.stats["total_found"] += 1

                    if count % 50 == 0:
                        logger.info("search_progress", query=query, collected=count)

                logger.info("search_completed", query=query, found=count)

            except Exception as e:
                logger.error("search_failed", query=query, error=str(e))
                self.stats["errors"] += 1

        self.stats["total_collected"] = len(all_repos)
        return all_repos

    async def collect_repository_details(
        self,
        owner: str,
        repo: str,
    ) -> Optional[RepositoryCreate]:
        """Collect detailed repository information."""
        if not self.client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        try:
            # Get basic repo info
            repo_data = await self.client.get_repository(owner, repo)
            
            # Get languages
            languages = await self.client.get_repository_languages(owner, repo)
            repo_data["languages"] = languages
            
            # Get topics
            topics = await self.client.get_repository_topics(owner, repo)
            repo_data["topics"] = topics

            return self._parse_repository(repo_data)

        except Exception as e:
            logger.error("collect_repo_details_failed", owner=owner, repo=repo, error=str(e))
            self.stats["errors"] += 1
            return None

    async def enrich_repositories(
        self,
        repositories: List[RepositoryCreate],
    ) -> List[RepositoryCreate]:
        """Enrich repositories with languages and topics."""
        if not self.client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        enriched = []
        for repo in repositories:
            try:
                owner, name = repo.full_name.split("/", 1)
                
                # Get languages
                languages = await self.client.get_repository_languages(owner, name)
                repo.languages = languages
                
                # Get topics
                topics = await self.client.get_repository_topics(owner, name)
                repo.topics = topics
                
                # Recalculate AI/ML classification
                ai_ml_topics = [t for t in topics if t.lower() in settings.ai_ml_topics]
                repo.is_ai_ml_repo = len(ai_ml_topics) > 0
                repo.ai_ml_topics = ai_ml_topics

                enriched.append(repo)
                
                # Rate limiting
                await asyncio.sleep(settings.collection_rate_limit_delay)

            except Exception as e:
                logger.error("enrich_failed", repo=repo.full_name, error=str(e))
                enriched.append(repo)  # Keep original
                self.stats["errors"] += 1

        return enriched

    def get_stats(self) -> Dict[str, int]:
        """Get collection statistics."""
        return self.stats.copy()


async def collect_repositories(
    queries: Optional[List[str]] = None,
    max_per_query: Optional[int] = None,
) -> List[RepositoryCreate]:
    """Convenience function to collect repositories."""
    async with RepositoryCollector() as collector:
        return await collector.collect_from_search(queries, max_per_query)