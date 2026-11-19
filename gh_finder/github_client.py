# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/
#
# Original Author: Sergio Palma Hidalgo
# Project URL: https://github.com/del-Pacifico/gh-finder
# Copyright (c) 2025 Sergio Palma Hidalgo
# All rights reserved.
# github_client.py - gh-finder

"""GitHub API client for gh-finder."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

import platformdirs
import requests

from gh_finder.models import RepoResult

logger = logging.getLogger(__name__)

GITHUB_API_SEARCH_URL = "https://api.github.com/search/repositories"
GITHUB_API_RATE_LIMIT_URL = "https://api.github.com/rate_limit"
CACHE_TTL_SECONDS = 300  # 5 minutes
DEFAULT_TIMEOUT_SECONDS = 15


class GitHubClientError(Exception):
    """Base exception for GitHub client errors."""


class RateLimitError(GitHubClientError):
    """Raised when GitHub rate limit is exceeded."""


class QueryError(GitHubClientError):
    """Raised when GitHub rejects the search query (422)."""


class ServerError(GitHubClientError):
    """Raised when GitHub returns a 5xx server error."""


class NetworkError(GitHubClientError):
    """Raised when GitHub cannot be reached (timeout or connection failure)."""


def _build_headers(token: str | None) -> dict[str, str]:
    """Build HTTP headers for GitHub API requests."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "gh-finder",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_cache_dir() -> Path:
    """Return the cache directory, creating it if necessary."""
    cache_dir = Path(platformdirs.user_cache_dir("gh-finder"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _get_cache_path(query: str, limit: int, has_token: bool) -> Path:
    """Return the cache file path for a given query signature."""
    signature = f"{query}|{limit}|{has_token}"
    digest = hashlib.sha256(signature.encode("utf-8")).hexdigest()[:16]
    return _get_cache_dir() / f"{digest}.json"


def _read_cache(path: Path) -> dict[str, Any] | None:
    """Read a cache entry if it exists and is not expired."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    timestamp = data.get("timestamp", 0)
    age = time.time() - timestamp
    if age > CACHE_TTL_SECONDS:
        try:
            path.unlink()
        except OSError:
            pass
        return None

    logger.debug("[gh-finder] Cache hit (age: %ds): %s", int(age), path)
    return data.get("payload")


def _write_cache(path: Path, payload: dict[str, Any]) -> None:
    """Write a payload to cache with the current timestamp."""
    try:
        data = {"timestamp": time.time(), "payload": payload}
        path.write_text(json.dumps(data), encoding="utf-8")
        logger.debug("[gh-finder] Cache written: %s", path)
    except OSError as exc:
        logger.debug("[gh-finder] Could not write cache: %s", exc)


def _handle_403(response: requests.Response) -> None:
    """Translate a 403 response into an actionable RateLimitError."""
    remaining = response.headers.get("X-RateLimit-Remaining")
    retry_after = response.headers.get("Retry-After")
    reset_time = response.headers.get("X-RateLimit-Reset", "unknown")

    if remaining == "0":
        raise RateLimitError(
            f"GitHub rate limit exceeded. You have 0 requests left until "
            f"timestamp {reset_time}. Set the GITHUB_TOKEN environment variable "
            f"to increase your limit from 60 to 5,000 requests/hour."
        )
    if retry_after:
        raise RateLimitError(
            f"GitHub secondary rate limit triggered. Wait {retry_after} seconds "
            f"and try again."
        )
    raise RateLimitError(
        "GitHub returned 403. This may be a rate limit or a secondary limit "
        "triggered by rapid requests. Wait a moment and try again."
    )


def _raise_for_status(response: requests.Response) -> None:
    """Translate non-2xx responses into specific exceptions."""
    if response.status_code == 200:
        return
    if response.status_code == 403:
        _handle_403(response)
    if response.status_code == 422:
        try:
            message = response.json().get("message", "Invalid query.")
        except ValueError:
            message = "Invalid query."
        raise QueryError(
            f"GitHub rejected the search query: {message}. "
            f"Check your syntax or run with --dry-run to see the generated query."
        )
    if 500 <= response.status_code < 600:
        raise ServerError(
            f"GitHub returned a server error ({response.status_code}). "
            f"This is not a problem with gh-finder. Try again in a few minutes."
        )
    raise GitHubClientError(
        f"Unexpected response from GitHub ({response.status_code})."
    )


def search_repositories(
    query: str,
    limit: int = 10,
    token: str | None = None,
    use_cache: bool = True,
    verbose: bool = False,
) -> list[RepoResult]:
    """Search GitHub repositories and return a list of RepoResult.

    Results are cached on disk for 5 minutes unless use_cache is False.
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    cache_path = _get_cache_path(query, limit, bool(token))
    if use_cache:
        cached = _read_cache(cache_path)
        if cached is not None:
            return [RepoResult.from_api_payload(item) for item in cached.get("items", [])]

    params = {"q": query, "per_page": limit}
    if verbose:
        logger.debug("[gh-finder] GET %s params=%s", GITHUB_API_SEARCH_URL, params)

    start = time.time()
    try:
        response = requests.get(
            GITHUB_API_SEARCH_URL,
            headers=_build_headers(token),
            params=params,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except requests.Timeout as exc:
        raise NetworkError(
            "Could not reach GitHub: request timed out. "
            "Check your network connection and try again."
        ) from exc
    except requests.RequestException as exc:
        raise NetworkError(
            f"Could not reach GitHub: {exc}. "
            f"Check your network connection and try again."
        ) from exc

    elapsed = time.time() - start
    if verbose:
        remaining = response.headers.get("X-RateLimit-Remaining", "?")
        logger.debug(
            "[gh-finder] Status: %d | Time: %.2fs | Remaining: %s",
            response.status_code,
            elapsed,
            remaining,
        )

    _raise_for_status(response)

    try:
        payload = response.json()
    except ValueError as exc:
        raise GitHubClientError("GitHub returned a non-JSON response.") from exc

    if use_cache:
        _write_cache(cache_path, payload)

    return [RepoResult.from_api_payload(item) for item in payload.get("items", [])]


def check_rate_limit(token: str | None = None) -> dict[str, Any]:
    """Query GitHub's /rate_limit endpoint. Does not consume search quota."""
    try:
        response = requests.get(
            GITHUB_API_RATE_LIMIT_URL,
            headers=_build_headers(token),
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise NetworkError(
            f"Could not reach GitHub: {exc}. "
            f"Check your network connection and try again."
        ) from exc

    _raise_for_status(response)
    return response.json()