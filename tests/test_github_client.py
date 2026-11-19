# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/
#
# Original Author: Sergio Palma Hidalgo
# Project URL: https://github.com/del-Pacifico/gh-finder
# Copyright (c) 2025 Sergio Palma Hidalgo
# All rights reserved.
# test_github_client.py - gh-finder

"""Tests for gh_finder.github_client."""

from unittest.mock import Mock, patch

import pytest
import requests

from gh_finder.github_client import (
    GitHubClientError,
    NetworkError,
    QueryError,
    RateLimitError,
    ServerError,
    check_rate_limit,
    search_repositories,
)


def _mock_response(status_code=200, json_data=None, headers=None):
    response = Mock(spec=requests.Response)
    response.status_code = status_code
    response.headers = headers or {}
    response.json = Mock(return_value=json_data or {})
    return response


def _sample_payload():
    return {
        "items": [
            {
                "full_name": "owner/repo",
                "html_url": "https://github.com/owner/repo",
                "description": "Test repo",
                "language": "Python",
                "stargazers_count": 100,
                "forks_count": 10,
                "open_issues_count": 2,
                "pushed_at": "2025-01-01T00:00:00Z",
                "created_at": "2020-01-01T00:00:00Z",
                "topics": ["cli"],
                "license": {"spdx_id": "MIT"},
            }
        ]
    }


@patch("gh_finder.github_client.requests.get")
def test_search_success(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "gh_finder.github_client._get_cache_dir", lambda: tmp_path
    )
    mock_get.return_value = _mock_response(200, _sample_payload())

    results = search_repositories("language:python", limit=10, use_cache=False)

    assert len(results) == 1
    assert results[0].full_name == "owner/repo"
    assert results[0].stargazers_count == 100


@patch("gh_finder.github_client.requests.get")
def test_search_rate_limit_primary(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "gh_finder.github_client._get_cache_dir", lambda: tmp_path
    )
    mock_get.return_value = _mock_response(
        403, headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1234567890"}
    )

    with pytest.raises(RateLimitError, match="rate limit exceeded"):
        search_repositories("language:python", use_cache=False)


@patch("gh_finder.github_client.requests.get")
def test_search_rate_limit_secondary(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "gh_finder.github_client._get_cache_dir", lambda: tmp_path
    )
    mock_get.return_value = _mock_response(403, headers={"Retry-After": "60"})

    with pytest.raises(RateLimitError, match="secondary rate limit"):
        search_repositories("language:python", use_cache=False)


@patch("gh_finder.github_client.requests.get")
def test_search_invalid_query(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "gh_finder.github_client._get_cache_dir", lambda: tmp_path
    )
    mock_get.return_value = _mock_response(
        422, json_data={"message": "Validation Failed"}
    )

    with pytest.raises(QueryError, match="Validation Failed"):
        search_repositories("invalid query", use_cache=False)


@patch("gh_finder.github_client.requests.get")
def test_search_server_error(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "gh_finder.github_client._get_cache_dir", lambda: tmp_path
    )
    mock_get.return_value = _mock_response(500)

    with pytest.raises(ServerError, match="server error"):
        search_repositories("language:python", use_cache=False)


@patch("gh_finder.github_client.requests.get")
def test_search_timeout(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "gh_finder.github_client._get_cache_dir", lambda: tmp_path
    )
    mock_get.side_effect = requests.Timeout("timed out")

    with pytest.raises(NetworkError, match="timed out"):
        search_repositories("language:python", use_cache=False)


@patch("gh_finder.github_client.requests.get")
def test_search_unexpected_status(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "gh_finder.github_client._get_cache_dir", lambda: tmp_path
    )
    mock_get.return_value = _mock_response(418)

    with pytest.raises(GitHubClientError, match="Unexpected response"):
        search_repositories("language:python", use_cache=False)


@patch("gh_finder.github_client.requests.get")
def test_cache_hit_skips_request(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "gh_finder.github_client._get_cache_dir", lambda: tmp_path
    )
    mock_get.return_value = _mock_response(200, _sample_payload())

    first = search_repositories("language:python", limit=10, use_cache=True)
    second = search_repositories("language:python", limit=10, use_cache=True)

    assert len(first) == 1
    assert len(second) == 1
    assert mock_get.call_count == 1  # second call served from cache


@patch("gh_finder.github_client.requests.get")
def test_no_cache_forces_request(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "gh_finder.github_client._get_cache_dir", lambda: tmp_path
    )
    mock_get.return_value = _mock_response(200, _sample_payload())

    search_repositories("language:python", limit=10, use_cache=True)
    search_repositories("language:python", limit=10, use_cache=False)

    assert mock_get.call_count == 2


@patch("gh_finder.github_client.requests.get")
def test_check_rate_limit(mock_get):
    mock_get.return_value = _mock_response(
        200,
        json_data={"resources": {"search": {"remaining": 47, "limit": 60}}},
    )

    data = check_rate_limit(token=None)

    assert data["resources"]["search"]["remaining"] == 47
    mock_get.assert_called_once()