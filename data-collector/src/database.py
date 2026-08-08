# GitHub AI Repository Analytics - Database Layer
import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional
import asyncpg
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text
import structlog

from .config import settings
from .logging_config import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._pool: Optional[asyncpg.Pool] = None

    async def initialize(self) -> None:
        """Initialize database connections."""
        # SQLAlchemy async engine for ORM operations
        self._engine = create_async_engine(
            settings.postgres_async_dsn,
            pool_size=settings.postgres_pool_size,
            max_overflow=settings.postgres_max_overflow,
            pool_pre_ping=True,
            echo=False,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # asyncpg pool for high-performance raw queries
        self._pool = await asyncpg.create_pool(
            dsn=settings.postgres_dsn,
            min_size=5,
            max_size=settings.postgres_pool_size,
            command_timeout=60,
        )

        logger.info("database_initialized")

    async def close(self) -> None:
        """Close database connections."""
        if self._engine:
            await self._engine.dispose()
        if self._pool:
            await self._pool.close()
        logger.info("database_closed")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session."""
        if not self._session_factory:
            await self.initialize()
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a raw asyncpg connection."""
        if not self._pool:
            await self.initialize()
        async with self._pool.acquire() as conn:
            yield conn

    async def execute_raw(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute raw SQL query and return results as list of dicts."""
        async with self.connection() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def execute_raw_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute raw SQL query and return single result as dict."""
        async with self.connection() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def execute_many(self, query: str, args_list: List[tuple]) -> None:
        """Execute many parameterized queries."""
        async with self.connection() as conn:
            await conn.executemany(query, args_list)

    async def copy_records_to_table(
        self,
        table_name: str,
        records: List[Dict[str, Any]],
        columns: List[str],
    ) -> int:
        """Bulk insert records using COPY for high performance."""
        if not records:
            return 0

        async with self.connection() as conn:
            # Convert records to tuples in column order
            data = [tuple(record.get(col) for col in columns) for record in records]
            
            # Use COPY for bulk insert
            await conn.copy_records_to_table(
                table_name,
                records=data,
                columns=columns,
            )
            return len(records)

    async def upsert_repositories(self, repositories: List[Dict[str, Any]]) -> int:
        """Upsert repositories into raw.repositories table."""
        if not repositories:
            return 0

        columns = [
            "id", "node_id", "name", "full_name", "owner_login", "owner_type",
            "owner_id", "description", "homepage", "html_url", "api_url",
            "clone_url", "ssh_url", "git_url", "svn_url", "language",
            "languages_json", "topics", "topics_search", "default_branch",
            "license_key", "license_name", "license_spdx_id", "license_url",
            "is_private", "is_fork", "is_archived", "is_disabled", "is_template",
            "has_issues", "has_projects", "has_wiki", "has_pages", "has_downloads",
            "has_discussions", "archived_at", "pushed_at", "created_at", "updated_at",
            "size_kb", "stargazers_count", "watchers_count", "forks_count",
            "open_issues_count", "subscribers_count", "network_count",
            "contributors_count", "releases_count", "commits_count",
            "dependencies_count", "dependents_count", "collected_at", "raw_data"
        ]

        # Convert to tuples
        data = []
        for repo in repositories:
            row = (
                repo["id"], repo["node_id"], repo["name"], repo["full_name"],
                repo["owner_login"], repo["owner_type"], repo["owner_id"],
                repo.get("description"), repo.get("homepage"), repo["html_url"],
                repo["api_url"], repo["clone_url"], repo["ssh_url"],
                repo["git_url"], repo["svn_url"], repo.get("language"),
                repo.get("languages", {}), repo.get("topics", []),
                " ".join(repo.get("topics", [])), repo["default_branch"],
                repo.get("license_key"), repo.get("license_name"),
                repo.get("license_spdx_id"), repo.get("license_url"),
                repo["is_private"], repo["is_fork"], repo["is_archived"],
                repo["is_disabled"], repo["is_template"], repo["has_issues"],
                repo["has_projects"], repo["has_wiki"], repo["has_pages"],
                repo["has_downloads"], repo["has_discussions"],
                repo.get("archived_at"), repo.get("pushed_at"),
                repo["created_at"], repo["updated_at"], repo["size_kb"],
                repo["stargazers_count"], repo["watchers_count"],
                repo["forks_count"], repo["open_issues_count"],
                repo["subscribers_count"], repo["network_count"],
                repo.get("contributors_count", 0), repo.get("releases_count", 0),
                repo.get("commits_count", 0), repo.get("dependencies_count", 0),
                repo.get("dependents_count", 0), repo["collected_at"],
                repo.get("raw_data", {})
            )
            data.append(row)

        async with self.connection() as conn:
            await conn.executemany(
                f"""
                INSERT INTO raw.repositories ({", ".join(columns)})
                VALUES ({", ".join([f"${i+1}" for i in range(len(columns))])})
                ON CONFLICT (id) DO UPDATE SET
                    node_id = EXCLUDED.node_id,
                    name = EXCLUDED.name,
                    full_name = EXCLUDED.full_name,
                    owner_login = EXCLUDED.owner_login,
                    owner_type = EXCLUDED.owner_type,
                    owner_id = EXCLUDED.owner_id,
                    description = EXCLUDED.description,
                    homepage = EXCLUDED.homepage,
                    html_url = EXCLUDED.html_url,
                    api_url = EXCLUDED.api_url,
                    clone_url = EXCLUDED.clone_url,
                    ssh_url = EXCLUDED.ssh_url,
                    git_url = EXCLUDED.git_url,
                    svn_url = EXCLUDED.svn_url,
                    language = EXCLUDED.language,
                    languages_json = EXCLUDED.languages_json,
                    topics = EXCLUDED.topics,
                    topics_search = EXCLUDED.topics_search,
                    default_branch = EXCLUDED.default_branch,
                    license_key = EXCLUDED.license_key,
                    license_name = EXCLUDED.license_name,
                    license_spdx_id = EXCLUDED.license_spdx_id,
                    license_url = EXCLUDED.license_url,
                    is_private = EXCLUDED.is_private,
                    is_fork = EXCLUDED.is_fork,
                    is_archived = EXCLUDED.is_archived,
                    is_disabled = EXCLUDED.is_disabled,
                    is_template = EXCLUDED.is_template,
                    has_issues = EXCLUDED.has_issues,
                    has_projects = EXCLUDED.has_projects,
                    has_wiki = EXCLUDED.has_wiki,
                    has_pages = EXCLUDED.has_pages,
                    has_downloads = EXCLUDED.has_downloads,
                    has_discussions = EXCLUDED.has_discussions,
                    archived_at = EXCLUDED.archived_at,
                    pushed_at = EXCLUDED.pushed_at,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at,
                    size_kb = EXCLUDED.size_kb,
                    stargazers_count = EXCLUDED.stargazers_count,
                    watchers_count = EXCLUDED.watchers_count,
                    forks_count = EXCLUDED.forks_count,
                    open_issues_count = EXCLUDED.open_issues_count,
                    subscribers_count = EXCLUDED.subscribers_count,
                    network_count = EXCLUDED.network_count,
                    contributors_count = EXCLUDED.contributors_count,
                    releases_count = EXCLUDED.releases_count,
                    commits_count = EXCLUDED.commits_count,
                    dependencies_count = EXCLUDED.dependencies_count,
                    dependents_count = EXCLUDED.dependents_count,
                    collected_at = EXCLUDED.collected_at,
                    raw_data = EXCLUDED.raw_data
                """,
                data,
            )
        return len(data)

    async def upsert_contributors(self, contributors: List[Dict[str, Any]]) -> int:
        """Upsert contributors into raw.contributors table."""
        if not contributors:
            return 0

        columns = [
            "repo_id", "contributor_id", "contributor_login", "contributor_name",
            "contributor_email", "contributor_company", "contributor_location",
            "contributor_bio", "contributor_avatar_url", "contributor_html_url",
            "contributor_type", "contributor_site_admin", "contributions_count",
            "additions", "deletions", "commit_count", "first_contribution_date",
            "last_contribution_date", "is_organization_member", "collected_at", "raw_data"
        ]

        data = []
        for contrib in contributors:
            row = (
                contrib["repo_id"], contrib["contributor_id"], contrib["contributor_login"],
                contrib.get("contributor_name"), contrib.get("contributor_email"),
                contrib.get("contributor_company"), contrib.get("contributor_location"),
                contrib.get("contributor_bio"), contrib["contributor_avatar_url"],
                contrib["contributor_html_url"], contrib["contributor_type"],
                contrib["contributor_site_admin"], contrib["contributions_count"],
                contrib.get("additions", 0), contrib.get("deletions", 0),
                contrib.get("commit_count", 0), contrib.get("first_contribution_date"),
                contrib.get("last_contribution_date"), contrib["is_organization_member"],
                contrib["collected_at"], contrib.get("raw_data", {})
            )
            data.append(row)

        async with self.connection() as conn:
            await conn.executemany(
                f"""
                INSERT INTO raw.contributors ({", ".join(columns)})
                VALUES ({", ".join([f"${i+1}" for i in range(len(columns))])})
                ON CONFLICT (repo_id, contributor_id) DO UPDATE SET
                    contributor_login = EXCLUDED.contributor_login,
                    contributor_name = EXCLUDED.contributor_name,
                    contributor_email = EXCLUDED.contributor_email,
                    contributor_company = EXCLUDED.contributor_company,
                    contributor_location = EXCLUDED.contributor_location,
                    contributor_bio = EXCLUDED.contributor_bio,
                    contributor_avatar_url = EXCLUDED.contributor_avatar_url,
                    contributor_html_url = EXCLUDED.contributor_html_url,
                    contributor_type = EXCLUDED.contributor_type,
                    contributor_site_admin = EXCLUDED.contributor_site_admin,
                    contributions_count = EXCLUDED.contributions_count,
                    additions = EXCLUDED.additions,
                    deletions = EXCLUDED.deletions,
                    commit_count = EXCLUDED.commit_count,
                    first_contribution_date = EXCLUDED.first_contribution_date,
                    last_contribution_date = EXCLUDED.last_contribution_date,
                    is_organization_member = EXCLUDED.is_organization_member,
                    collected_at = EXCLUDED.collected_at,
                    raw_data = EXCLUDED.raw_data
                """,
                data,
            )
        return len(data)

    async def upsert_commits(self, commits: List[Dict[str, Any]]) -> int:
        """Upsert commits into raw.commits table."""
        if not commits:
            return 0

        columns = [
            "repo_id", "sha", "node_id", "author_id", "author_login", "author_name",
            "author_email", "author_date", "committer_id", "committer_login",
            "committer_name", "committer_email", "committer_date", "message",
            "message_headline", "additions", "deletions", "total_changes",
            "files_changed", "parents_sha", "is_merge", "collected_at", "raw_data"
        ]

        data = []
        for commit in commits:
            row = (
                commit["repo_id"], commit["sha"], commit.get("node_id"),
                commit.get("author_id"), commit.get("author_login"),
                commit.get("author_name"), commit.get("author_email"),
                commit["author_date"], commit.get("committer_id"),
                commit.get("committer_login"), commit.get("committer_name"),
                commit.get("committer_email"), commit["committer_date"],
                commit["message"], commit.get("message_headline"),
                commit["additions"], commit["deletions"], commit["total_changes"],
                commit["files_changed"], commit.get("parents_sha", []),
                commit["is_merge"], commit["collected_at"], commit.get("raw_data", {})
            )
            data.append(row)

        async with self.connection() as conn:
            await conn.executemany(
                f"""
                INSERT INTO raw.commits ({", ".join(columns)})
                VALUES ({", ".join([f"${i+1}" for i in range(len(columns))])})
                ON CONFLICT (repo_id, sha) DO UPDATE SET
                    node_id = EXCLUDED.node_id,
                    author_id = EXCLUDED.author_id,
                    author_login = EXCLUDED.author_login,
                    author_name = EXCLUDED.author_name,
                    author_email = EXCLUDED.author_email,
                    author_date = EXCLUDED.author_date,
                    committer_id = EXCLUDED.committer_id,
                    committer_login = EXCLUDED.committer_login,
                    committer_name = EXCLUDED.committer_name,
                    committer_email = EXCLUDED.committer_email,
                    committer_date = EXCLUDED.committer_date,
                    message = EXCLUDED.message,
                    message_headline = EXCLUDED.message_headline,
                    additions = EXCLUDED.additions,
                    deletions = EXCLUDED.deletions,
                    total_changes = EXCLUDED.total_changes,
                    files_changed = EXCLUDED.files_changed,
                    parents_sha = EXCLUDED.parents_sha,
                    is_merge = EXCLUDED.is_merge,
                    collected_at = EXCLUDED.collected_at,
                    raw_data = EXCLUDED.raw_data
                """,
                data,
            )
        return len(data)

    async def upsert_issues(self, issues: List[Dict[str, Any]]) -> int:
        """Upsert issues into raw.issues table."""
        if not issues:
            return 0

        columns = [
            "repo_id", "issue_id", "node_id", "number", "title", "body", "state",
            "state_reason", "author_id", "author_login", "author_type",
            "assignee_id", "assignee_login", "assignees", "labels", "milestone_id",
            "milestone_title", "milestone_state", "comments_count", "reactions",
            "is_pull_request", "pull_request_url", "closed_at", "created_at",
            "updated_at", "collected_at", "raw_data"
        ]

        data = []
        for issue in issues:
            row = (
                issue["repo_id"], issue["issue_id"], issue.get("node_id"),
                issue["number"], issue["title"], issue.get("body"), issue["state"],
                issue.get("state_reason"), issue.get("author_id"),
                issue.get("author_login"), issue.get("author_type"),
                issue.get("assignee_id"), issue.get("assignee_login"),
                issue.get("assignees", []), issue.get("labels", []),
                issue.get("milestone_id"), issue.get("milestone_title"),
                issue.get("milestone_state"), issue["comments_count"],
                issue.get("reactions", {}), issue["is_pull_request"],
                issue.get("pull_request_url"), issue.get("closed_at"),
                issue["created_at"], issue["updated_at"], issue["collected_at"],
                issue.get("raw_data", {})
            )
            data.append(row)

        async with self.connection() as conn:
            await conn.executemany(
                f"""
                INSERT INTO raw.issues ({", ".join(columns)})
                VALUES ({", ".join([f"${i+1}" for i in range(len(columns))])})
                ON CONFLICT (repo_id, issue_id) DO UPDATE SET
                    node_id = EXCLUDED.node_id,
                    number = EXCLUDED.number,
                    title = EXCLUDED.title,
                    body = EXCLUDED.body,
                    state = EXCLUDED.state,
                    state_reason = EXCLUDED.state_reason,
                    author_id = EXCLUDED.author_id,
                    author_login = EXCLUDED.author_login,
                    author_type = EXCLUDED.author_type,
                    assignee_id = EXCLUDED.assignee_id,
                    assignee_login = EXCLUDED.assignee_login,
                    assignees = EXCLUDED.assignees,
                    labels = EXCLUDED.labels,
                    milestone_id = EXCLUDED.milestone_id,
                    milestone_title = EXCLUDED.milestone_title,
                    milestone_state = EXCLUDED.milestone_state,
                    comments_count = EXCLUDED.comments_count,
                    reactions = EXCLUDED.reactions,
                    is_pull_request = EXCLUDED.is_pull_request,
                    pull_request_url = EXCLUDED.pull_request_url,
                    closed_at = EXCLUDED.closed_at,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at,
                    collected_at = EXCLUDED.collected_at,
                    raw_data = EXCLUDED.raw_data
                """,
                data,
            )
        return len(data)

    async def upsert_pull_requests(self, prs: List[Dict[str, Any]]) -> int:
        """Upsert pull requests into raw.pull_requests table."""
        if not prs:
            return 0

        columns = [
            "repo_id", "pr_id", "node_id", "number", "title", "body", "state",
            "draft", "author_id", "author_login", "author_type", "assignee_id",
            "assignee_login", "assignees", "reviewers", "labels", "milestone_id",
            "milestone_title", "base_ref", "base_sha", "head_ref", "head_sha",
            "head_repo_id", "head_repo_full_name", "comments_count",
            "review_comments_count", "commits_count", "additions", "deletions",
            "changed_files", "mergeable", "mergeable_state", "merged", "merged_at",
            "merged_by_id", "merged_by_login", "closed_at", "created_at",
            "updated_at", "collected_at", "raw_data"
        ]

        data = []
        for pr in prs:
            row = (
                pr["repo_id"], pr["pr_id"], pr.get("node_id"), pr["number"],
                pr["title"], pr.get("body"), pr["state"], pr["draft"],
                pr.get("author_id"), pr.get("author_login"), pr.get("author_type"),
                pr.get("assignee_id"), pr.get("assignee_login"),
                pr.get("assignees", []), pr.get("reviewers", []),
                pr.get("labels", []), pr.get("milestone_id"),
                pr.get("milestone_title"), pr.get("base_ref"), pr.get("base_sha"),
                pr.get("head_ref"), pr.get("head_sha"), pr.get("head_repo_id"),
                pr.get("head_repo_full_name"), pr["comments_count"],
                pr["review_comments_count"], pr["commits_count"],
                pr["additions"], pr["deletions"], pr["changed_files"],
                pr.get("mergeable"), pr.get("mergeable_state"), pr["merged"],
                pr.get("merged_at"), pr.get("merged_by_id"),
                pr.get("merged_by_login"), pr.get("closed_at"),
                pr["created_at"], pr["updated_at"], pr["collected_at"],
                pr.get("raw_data", {})
            )
            data.append(row)

        async with self.connection() as conn:
            await conn.executemany(
                f"""
                INSERT INTO raw.pull_requests ({", ".join(columns)})
                VALUES ({", ".join([f"${i+1}" for i in range(len(columns))])})
                ON CONFLICT (repo_id, pr_id) DO UPDATE SET
                    node_id = EXCLUDED.node_id,
                    number = EXCLUDED.number,
                    title = EXCLUDED.title,
                    body = EXCLUDED.body,
                    state = EXCLUDED.state,
                    draft = EXCLUDED.draft,
                    author_id = EXCLUDED.author_id,
                    author_login = EXCLUDED.author_login,
                    author_type = EXCLUDED.author_type,
                    assignee_id = EXCLUDED.assignee_id,
                    assignee_login = EXCLUDED.assignee_login,
                    assignees = EXCLUDED.assignees,
                    reviewers = EXCLUDED.reviewers,
                    labels = EXCLUDED.labels,
                    milestone_id = EXCLUDED.milestone_id,
                    milestone_title = EXCLUDED.milestone_title,
                    base_ref = EXCLUDED.base_ref,
                    base_sha = EXCLUDED.base_sha,
                    head_ref = EXCLUDED.head_ref,
                    head_sha = EXCLUDED.head_sha,
                    head_repo_id = EXCLUDED.head_repo_id,
                    head_repo_full_name = EXCLUDED.head_repo_full_name,
                    comments_count = EXCLUDED.comments_count,
                    review_comments_count = EXCLUDED.review_comments_count,
                    commits_count = EXCLUDED.commits_count,
                    additions = EXCLUDED.additions,
                    deletions = EXCLUDED.deletions,
                    changed_files = EXCLUDED.changed_files,
                    mergeable = EXCLUDED.mergeable,
                    mergeable_state = EXCLUDED.mergeable_state,
                    merged = EXCLUDED.merged,
                    merged_at = EXCLUDED.merged_at,
                    merged_by_id = EXCLUDED.merged_by_id,
                    merged_by_login = EXCLUDED.merged_by_login,
                    closed_at = EXCLUDED.closed_at,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at,
                    collected_at = EXCLUDED.collected_at,
                    raw_data = EXCLUDED.raw_data
                """,
                data,
            )
        return len(data)

    async def upsert_releases(self, releases: List[Dict[str, Any]]) -> int:
        """Upsert releases into raw.releases table."""
        if not releases:
            return 0

        columns = [
            "repo_id", "release_id", "node_id", "tag_name", "target_commitish",
            "name", "body", "draft", "prerelease", "author_id", "author_login",
            "author_type", "assets", "tarball_url", "zipball_url", "html_url",
            "created_at", "published_at", "collected_at", "raw_data"
        ]

        data = []
        for release in releases:
            row = (
                release["repo_id"], release["release_id"], release.get("node_id"),
                release["tag_name"], release.get("target_commitish"),
                release.get("name"), release.get("body"), release["draft"],
                release["prerelease"], release.get("author_id"),
                release.get("author_login"), release.get("author_type"),
                release.get("assets", []), release["tarball_url"],
                release["zipball_url"], release["html_url"],
                release["created_at"], release.get("published_at"),
                release["collected_at"], release.get("raw_data", {})
            )
            data.append(row)

        async with self.connection() as conn:
            await conn.executemany(
                f"""
                INSERT INTO raw.releases ({", ".join(columns)})
                VALUES ({", ".join([f"${i+1}" for i in range(len(columns))])})
                ON CONFLICT (repo_id, release_id) DO UPDATE SET
                    node_id = EXCLUDED.node_id,
                    tag_name = EXCLUDED.tag_name,
                    target_commitish = EXCLUDED.target_commitish,
                    name = EXCLUDED.name,
                    body = EXCLUDED.body,
                    draft = EXCLUDED.draft,
                    prerelease = EXCLUDED.prerelease,
                    author_id = EXCLUDED.author_id,
                    author_login = EXCLUDED.author_login,
                    author_type = EXCLUDED.author_type,
                    assets = EXCLUDED.assets,
                    tarball_url = EXCLUDED.tarball_url,
                    zipball_url = EXCLUDED.zipball_url,
                    html_url = EXCLUDED.html_url,
                    created_at = EXCLUDED.created_at,
                    published_at = EXCLUDED.published_at,
                    collected_at = EXCLUDED.collected_at,
                    raw_data = EXCLUDED.raw_data
                """,
                data,
            )
        return len(data)

    async def upsert_stargazers(self, stargazers: List[Dict[str, Any]]) -> int:
        """Upsert stargazers into raw.stargazers table."""
        if not stargazers:
            return 0

        columns = [
            "repo_id", "user_id", "user_login", "starred_at", "collected_at"
        ]

        data = []
        for star in stargazers:
            row = (
                star["repo_id"], star["user_id"], star["user_login"],
                star["starred_at"], star["collected_at"]
            )
            data.append(row)

        async with self.connection() as conn:
            await conn.executemany(
                f"""
                INSERT INTO raw.stargazers ({", ".join(columns)})
                VALUES ({", ".join([f"${i+1}" for i in range(len(columns))])})
                ON CONFLICT (repo_id, user_id) DO UPDATE SET
                    user_login = EXCLUDED.user_login,
                    starred_at = EXCLUDED.starred_at,
                    collected_at = EXCLUDED.collected_at
                """,
                data,
            )
        return len(data)

    async def get_repository_ids(self, limit: Optional[int] = None) -> List[int]:
        """Get repository IDs from raw.repositories."""
        query = "SELECT id FROM raw.repositories ORDER BY stargazers_count DESC"
        if limit:
            query += f" LIMIT {limit}"
        rows = await self.execute_raw(query)
        return [row["id"] for row in rows]

    async def get_repositories_for_collection(
        self,
        limit: Optional[int] = None,
        only_ai_ml: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get repositories that need data collection."""
        where_clause = "WHERE 1=1"
        if only_ai_ml:
            where_clause += " AND topics && ARRAY['machine-learning', 'deep-learning', 'artificial-intelligence', 'nlp', 'computer-vision', 'reinforcement-learning', 'llm', 'transformers']"
        
        query = f"""
            SELECT id, owner_login, name, full_name, topics
            FROM raw.repositories
            {where_clause}
            ORDER BY stargazers_count DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        
        return await self.execute_raw(query)


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> DatabaseManager:
    """Dependency for FastAPI to get database manager."""
    return db_manager