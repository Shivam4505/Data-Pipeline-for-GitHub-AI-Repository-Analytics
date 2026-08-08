# GitHub AI Repository Analytics - Data Collector Main Entry Point
import asyncio
import sys
from datetime import datetime, timedelta
from typing import List, Optional
import click
import structlog

from .config import settings
from .logging_config import setup_logging, get_logger
from .github_client import create_github_client
from .database import db_manager
from .collectors.repo_collector import RepositoryCollector, collect_repositories
from .collectors.contributor_collector import ContributorCollector, collect_contributors
from .collectors.commit_collector import CommitCollector, collect_commits
from .collectors.issue_pr_collector import IssuePRCollector, collect_issues_and_prs

logger = get_logger(__name__)


async def run_full_collection(
    max_repos: Optional[int] = None,
    since_days: Optional[int] = None,
    only_ai_ml: bool = True,
) -> dict:
    """Run full data collection pipeline."""
    logger.info("starting_full_collection", max_repos=max_repos, since_days=since_days, only_ai_ml=only_ai_ml)
    
    await db_manager.initialize()
    
    try:
        async with create_github_client() as client:
            # Step 1: Collect repositories
            logger.info("step_1_collecting_repositories")
            repo_collector = RepositoryCollector(client)
            repositories = await repo_collector.collect_from_search(
                max_per_query=max_repos or settings.max_repositories_per_run
            )
            
            if not repositories:
                logger.warning("no_repositories_found")
                return {"repositories": 0, "contributors": 0, "commits": 0, "issues": 0, "prs": 0}
            
            # Convert to dict for database
            repo_dicts = [repo.model_dump() for repo in repositories]
            await db_manager.upsert_repositories(repo_dicts)
            logger.info("repositories_stored", count=len(repo_dicts))
            
            # Get repo info for other collectors
            repo_infos = [
                {"id": r.id, "owner_login": r.owner_login, "name": r.name, "full_name": r.full_name}
                for r in repositories
            ]
            
            # Step 2: Collect contributors
            logger.info("step_2_collecting_contributors")
            contributor_collector = ContributorCollector(client)
            contributors_data = await contributor_collector.collect_for_repositories(repo_infos)
            
            all_contributors = []
            for contribs in contributors_data.values():
                all_contributors.extend([c.model_dump() for c in contribs])
            
            if all_contributors:
                await db_manager.upsert_contributors(all_contributors)
                logger.info("contributors_stored", count=len(all_contributors))
            
            # Step 3: Collect commits
            logger.info("step_3_collecting_commits")
            since = None
            if since_days:
                since = (datetime.utcnow() - timedelta(days=since_days)).isoformat()
            
            commit_collector = CommitCollector(client)
            commits_data = await commit_collector.collect_for_repositories(
                repo_infos, since=since
            )
            
            all_commits = []
            for commits in commits_data.values():
                all_commits.extend([c.model_dump() for c in commits])
            
            if all_commits:
                await db_manager.upsert_commits(all_commits)
                logger.info("commits_stored", count=len(all_commits))
            
            # Step 4: Collect issues and PRs
            logger.info("step_4_collecting_issues_prs")
            issue_pr_collector = IssuePRCollector(client)
            issues_prs_data = await issue_pr_collector.collect_for_repositories(
                repo_infos, since=since
            )
            
            all_issues = []
            all_prs = []
            for issues, prs in issues_prs_data.values():
                all_issues.extend([i.model_dump() for i in issues])
                all_prs.extend([p.model_dump() for p in prs])
            
            if all_issues:
                await db_manager.upsert_issues(all_issues)
                logger.info("issues_stored", count=len(all_issues))
            
            if all_prs:
                await db_manager.upsert_pull_requests(all_prs)
                logger.info("prs_stored", count=len(all_prs))
            
            # Summary
            summary = {
                "repositories": len(repo_dicts),
                "contributors": len(all_contributors),
                "commits": len(all_commits),
                "issues": len(all_issues),
                "prs": len(all_prs),
            }
            
            logger.info("collection_completed", **summary)
            return summary
            
    finally:
        await db_manager.close()


async def run_incremental_collection(
    since_days: int = 1,
    max_repos: Optional[int] = None,
) -> dict:
    """Run incremental collection for recent activity."""
    logger.info("starting_incremental_collection", since_days=since_days, max_repos=max_repos)
    
    await db_manager.initialize()
    
    try:
        # Get repositories to update
        repos = await db_manager.get_repositories_for_collection(
            limit=max_repos,
            only_ai_ml=True,
        )
        
        if not repos:
            logger.warning("no_repositories_for_incremental")
            return {"repositories": 0, "contributors": 0, "commits": 0, "issues": 0, "prs": 0}
        
        repo_infos = [
            {"id": r["id"], "owner_login": r["owner_login"], "name": r["name"], "full_name": r["full_name"]}
            for r in repos
        ]
        
        since = (datetime.utcnow() - timedelta(days=since_days)).isoformat()
        
        async with create_github_client() as client:
            # Collect recent commits
            commit_collector = CommitCollector(client)
            commits_data = await commit_collector.collect_for_repositories(
                repo_infos, since=since
            )
            
            all_commits = []
            for commits in commits_data.values():
                all_commits.extend([c.model_dump() for c in commits])
            
            if all_commits:
                await db_manager.upsert_commits(all_commits)
            
            # Collect recent issues and PRs
            issue_pr_collector = IssuePRCollector(client)
            issues_prs_data = await issue_pr_collector.collect_for_repositories(
                repo_infos, since=since
            )
            
            all_issues = []
            all_prs = []
            for issues, prs in issues_prs_data.values():
                all_issues.extend([i.model_dump() for i in issues])
                all_prs.extend([p.model_dump() for p in prs])
            
            if all_issues:
                await db_manager.upsert_issues(all_issues)
            
            if all_prs:
                await db_manager.upsert_pull_requests(all_prs)
            
            summary = {
                "repositories": len(repo_infos),
                "commits": len(all_commits),
                "issues": len(all_issues),
                "prs": len(all_prs),
            }
            
            logger.info("incremental_collection_completed", **summary)
            return summary
            
    finally:
        await db_manager.close()


@click.group()
@click.option("--log-level", default="INFO", help="Log level")
@click.option("--log-format", default="json", type=click.Choice(["json", "console"]), help="Log format")
def cli(log_level: str, log_format: str):
    """GitHub AI Repository Analytics Data Collector."""
    setup_logging(log_level, log_format)


@cli.command()
@click.option("--max-repos", type=int, help="Maximum repositories per query")
@click.option("--since-days", type=int, help="Collect data since N days ago")
@click.option("--only-ai-ml/--all-repos", default=True, help="Only collect AI/ML repositories")
def collect(max_repos: Optional[int], since_days: Optional[int], only_ai_ml: bool):
    """Run full data collection."""
    asyncio.run(run_full_collection(max_repos, since_days, only_ai_ml))


@cli.command()
@click.option("--since-days", default=1, type=int, help="Collect data since N days ago")
@click.option("--max-repos", type=int, help="Maximum repositories to process")
def incremental(since_days: int, max_repos: Optional[int]):
    """Run incremental collection for recent activity."""
    asyncio.run(run_incremental_collection(since_days, max_repos))


@cli.command()
@click.option("--queries", multiple=True, help="Custom search queries")
@click.option("--max-per-query", type=int, default=100, help="Max results per query")
def search(queries: List[str], max_per_query: int):
    """Search and collect repositories only."""
    async def _search():
        await db_manager.initialize()
        try:
            async with create_github_client() as client:
                collector = RepositoryCollector(client)
                repos = await collector.collect_from_search(
                    queries=list(queries) if queries else None,
                    max_per_query=max_per_query,
                )
                repo_dicts = [r.model_dump() for r in repos]
                await db_manager.upsert_repositories(repo_dicts)
                logger.info("search_collection_completed", count=len(repo_dicts))
        finally:
            await db_manager.close()
    
    asyncio.run(_search())


@cli.command()
def rate_limit():
    """Check GitHub API rate limit."""
    async def _check():
        async with create_github_client() as client:
            rate_limit = await client.get_rate_limit()
            logger.info("rate_limit", 
                limit=rate_limit.limit,
                remaining=rate_limit.remaining,
                reset_at=rate_limit.reset_at,
            )
            print(f"Limit: {rate_limit.limit}")
            print(f"Remaining: {rate_limit.remaining}")
            print(f"Resets at: {datetime.fromtimestamp(rate_limit.reset_at)}")
    
    asyncio.run(_check())


if __name__ == "__main__":
    cli()