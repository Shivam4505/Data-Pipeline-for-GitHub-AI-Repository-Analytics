# GitHub AI Repository Analytics - GitHub API Client
import asyncio
import time
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)
import structlog

from .config import settings
from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class RateLimitInfo:
    """GitHub API rate limit information."""
    limit: int
    remaining: int
    reset_at: float
    used: int
    resource: str = "core"

    @property
    def is_exhausted(self) -> bool:
        return self.remaining <= settings.github_rate_limit_buffer

    @property
    def seconds_until_reset(self) -> float:
        return max(0, self.reset_at - time.time())


class GitHubRateLimitError(Exception):
    """Raised when GitHub API rate limit is exceeded."""
    def __init__(self, rate_limit: RateLimitInfo):
        self.rate_limit = rate_limit
        super().__init__(
            f"GitHub API rate limit exceeded. Resets in {rate_limit.seconds_until_reset:.0f}s"
        )


class GitHubAPIError(Exception):
    """Raised for GitHub API errors."""
    def __init__(self, status_code: int, message: str, response: Optional[Dict] = None):
        self.status_code = status_code
        self.response = response
        super().__init__(f"GitHub API error {status_code}: {message}")


class GitHubClient:
    """Async GitHub API client with rate limiting and retry logic."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.github_token
        self.base_url = settings.github_api_base_url
        self.graphql_url = settings.github_graphql_url
        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limit: Optional[RateLimitInfo] = None
        self._rate_limit_lock = asyncio.Lock()

    async def __aenter__(self) -> "GitHubClient":
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "User-Agent": "GitHub-AI-Analytics/1.0",
                },
                timeout=httpx.Timeout(30.0, connect=10.0),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _update_rate_limit(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            self._rate_limit = RateLimitInfo(
                limit=int(headers.get("X-RateLimit-Limit", 5000)),
                remaining=int(headers.get("X-RateLimit-Remaining", 0)),
                reset_at=float(headers.get("X-RateLimit-Reset", time.time() + 3600)),
                used=int(headers.get("X-RateLimit-Used", 0)),
            )
        except (ValueError, TypeError):
            pass

    async def _wait_for_rate_limit(self) -> None:
        """Wait if rate limit is exhausted."""
        async with self._rate_limit_lock:
            if self._rate_limit and self._rate_limit.is_exhausted:
                wait_time = self._rate_limit.seconds_until_reset + 1
                logger.warning(
                    "rate_limit_exhausted",
                    remaining=self._rate_limit.remaining,
                    wait_time=wait_time,
                )
                await asyncio.sleep(wait_time)

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError, GitHubRateLimitError)),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, "WARNING"),
    )
    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> httpx.Response:
        """Make HTTP request with rate limiting and error handling."""
        await self._ensure_client()
        await self._wait_for_rate_limit()

        request_headers = headers or {}
        if method.upper() in ("POST", "PATCH", "PUT"):
            request_headers.setdefault("Content-Type", "application/json")

        response = await self._client.request(
            method=method,
            url=path,
            params=params,
            json=json,
            headers=request_headers,
        )

        self._update_rate_limit(response.headers)

        if response.status_code == 403 and "rate limit" in response.text.lower():
            raise GitHubRateLimitError(self._rate_limit or RateLimitInfo(0, 0, time.time() + 3600, 0))

        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("message", response.text)
            except Exception:
                message = response.text
            raise GitHubAPIError(response.status_code, message, error_data if 'error_data' in locals() else None)

        return response

    async def get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request returning JSON."""
        response = await self._request("GET", path, params=params)
        return response.json()

    async def post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        """POST request returning JSON."""
        response = await self._request("POST", path, json=json)
        return response.json()

    async def graphql(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute GraphQL query."""
        response = await self._request(
            "POST",
            self.graphql_url,
            json={"query": query, "variables": variables or {}},
        )
        data = response.json()
        if "errors" in data:
            raise GitHubAPIError(400, str(data["errors"]), data)
        return data.get("data", {})

    async def paginate(
        self,
        path: str,
        params: Optional[Dict] = None,
        per_page: int = 100,
        max_pages: Optional[int] = None,
    ) -> AsyncGenerator[List[Dict], None]:
        """Paginate through list endpoints."""
        page = 1
        current_params = params or {}
        current_params["per_page"] = min(per_page, 100)

        while True:
            current_params["page"] = page
            data = await self.get(path, params=current_params)

            if not data:
                break

            yield data

            if max_pages and page >= max_pages:
                break

            if len(data) < current_params["per_page"]:
                break

            page += 1
            await asyncio.sleep(settings.collection_rate_limit_delay)

    async def get_rate_limit(self) -> RateLimitInfo:
        """Get current rate limit status."""
        data = await self.get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        self._rate_limit = RateLimitInfo(
            limit=core.get("limit", 5000),
            remaining=core.get("remaining", 0),
            reset_at=core.get("reset", time.time() + 3600),
            used=core.get("used", 0),
        )
        return self._rate_limit

    # Repository methods
    async def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        per_page: int = 100,
        max_results: Optional[int] = None,
    ) -> AsyncGenerator[Dict, None]:
        """Search for repositories."""
        params = {"q": query, "sort": sort, "order": order, "per_page": per_page}
        count = 0
        async for page in self.paginate("/search/repositories", params=params):
            for repo in page.get("items", []):
                yield repo
                count += 1
                if max_results and count >= max_results:
                    return

    async def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository details."""
        return await self.get(f"/repos/{owner}/{repo}")

    async def get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get repository languages."""
        return await self.get(f"/repos/{owner}/{repo}/languages")

    async def get_repository_topics(self, owner: str, repo: str) -> List[str]:
        """Get repository topics."""
        data = await self.get(f"/repos/{owner}/{repo}/topics")
        return data.get("names", [])

    async def get_contributors(
        self,
        owner: str,
        repo: str,
        per_page: int = 100,
        max_results: Optional[int] = None,
    ) -> AsyncGenerator[Dict, None]:
        """Get repository contributors."""
        count = 0
        async for page in self.paginate(
            f"/repos/{owner}/{repo}/contributors",
            per_page=per_page,
        ):
            for contributor in page:
                yield contributor
                count += 1
                if max_results and count >= max_results:
                    return

    async def get_commits(
        self,
        owner: str,
        repo: str,
        since: Optional[str] = None,
        until: Optional[str] = None,
        per_page: int = 100,
        max_results: Optional[int] = None,
    ) -> AsyncGenerator[Dict, None]:
        """Get repository commits."""
        params = {"per_page": per_page}
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        count = 0
        async for page in self.paginate(f"/repos/{owner}/{repo}/commits", params=params):
            for commit in page:
                yield commit
                count += 1
                if max_results and count >= max_results:
                    return

    async def get_commit(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """Get single commit details."""
        return await self.get(f"/repos/{owner}/{repo}/commits/{sha}")

    async def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        since: Optional[str] = None,
        per_page: int = 100,
        max_results: Optional[int] = None,
    ) -> AsyncGenerator[Dict, None]:
        """Get repository issues (includes PRs)."""
        params = {"state": state, "per_page": per_page}
        if since:
            params["since"] = since

        count = 0
        async for page in self.paginate(f"/repos/{owner}/{repo}/issues", params=params):
            for issue in page:
                yield issue
                count += 1
                if max_results and count >= max_results:
                    return

    async def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        per_page: int = 100,
        max_results: Optional[int] = None,
    ) -> AsyncGenerator[Dict, None]:
        """Get repository pull requests."""
        params = {"state": state, "per_page": per_page}
        count = 0
        async for page in self.paginate(f"/repos/{owner}/{repo}/pulls", params=params):
            for pr in page:
                yield pr
                count += 1
                if max_results and count >= max_results:
                    return

    async def get_pull_request(self, owner: str, repo: str, number: int) -> Dict[str, Any]:
        """Get single pull request details."""
        return await self.get(f"/repos/{owner}/{repo}/pulls/{number}")

    async def get_releases(
        self,
        owner: str,
        repo: str,
        per_page: int = 100,
        max_results: Optional[int] = None,
    ) -> AsyncGenerator[Dict, None]:
        """Get repository releases."""
        count = 0
        async for page in self.paginate(f"/repos/{owner}/{repo}/releases", per_page=per_page):
            for release in page:
                yield release
                count += 1
                if max_results and count >= max_results:
                    return

    async def get_stargazers(
        self,
        owner: str,
        repo: str,
        per_page: int = 100,
        max_results: Optional[int] = None,
    ) -> AsyncGenerator[Dict, None]:
        """Get repository stargazers with timestamps."""
        headers = {"Accept": "application/vnd.github.star+json"}
        count = 0
        async for page in self.paginate(f"/repos/{owner}/{repo}/stargazers", per_page=per_page, headers=headers):
            for stargazer in page:
                yield stargazer
                count += 1
                if max_results and count >= max_results:
                    return

    async def get_user(self, username: str) -> Dict[str, Any]:
        """Get user profile."""
        return await self.get(f"/users/{username}")

    async def get_organization(self, org: str) -> Dict[str, Any]:
        """Get organization profile."""
        return await self.get(f"/orgs/{org}")


# Convenience function for creating client
async def create_github_client() -> GitHubClient:
    """Create and initialize GitHub client."""
    client = GitHubClient()
    await client._ensure_client()
    await client.get_rate_limit()
    return client