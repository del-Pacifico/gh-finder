# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/
#
# Original Author: Sergio Palma Hidalgo
# Project URL: https://github.com/del-Pacifico/gh-finder
# Copyright (c) 2025 Sergio Palma Hidalgo
# All rights reserved.
# test_models.py - gh-finder

"""Tests for gh_finder.models."""

from gh_finder.models import RepoResult


def test_from_api_payload_full():
    payload = {
        "full_name": "owner/repo",
        "html_url": "https://github.com/owner/repo",
        "description": "A test repository",
        "language": "Python",
        "stargazers_count": 1234,
        "pushed_at": "2025-01-15T10:00:00Z",
        "forks_count": 56,
        "open_issues_count": 7,
        "created_at": "2020-01-01T00:00:00Z",
        "topics": ["cli", "github"],
        "license": {"spdx_id": "MIT"},
    }
    repo = RepoResult.from_api_payload(payload)

    assert repo.full_name == "owner/repo"
    assert repo.html_url == "https://github.com/owner/repo"
    assert repo.description == "A test repository"
    assert repo.language == "Python"
    assert repo.stargazers_count == 1234
    assert repo.forks_count == 56
    assert repo.open_issues_count == 7
    assert repo.topics == ["cli", "github"]
    assert repo.license_spdx_id == "MIT"


def test_from_api_payload_missing_optional_fields():
    payload = {
        "full_name": "owner/minimal",
        "html_url": "https://github.com/owner/minimal",
    }
    repo = RepoResult.from_api_payload(payload)

    assert repo.full_name == "owner/minimal"
    assert repo.description is None
    assert repo.language is None
    assert repo.stargazers_count == 0
    assert repo.forks_count == 0
    assert repo.open_issues_count == 0
    assert repo.topics == []
    assert repo.license_spdx_id is None


def test_from_api_payload_null_fields():
    payload = {
        "full_name": "owner/repo",
        "html_url": "https://github.com/owner/repo",
        "description": None,
        "language": None,
        "stargazers_count": None,
        "forks_count": None,
        "open_issues_count": None,
        "topics": None,
        "license": None,
    }
    repo = RepoResult.from_api_payload(payload)

    assert repo.description is None
    assert repo.stargazers_count == 0
    assert repo.forks_count == 0
    assert repo.open_issues_count == 0
    assert repo.topics == []
    assert repo.license_spdx_id is None


def test_to_dict_roundtrip():
    repo = RepoResult(
        full_name="owner/repo",
        html_url="https://github.com/owner/repo",
        description="Test",
        language="Python",
        stargazers_count=10,
        topics=["cli"],
        license_spdx_id="MIT",
    )
    data = repo.to_dict()

    assert data["full_name"] == "owner/repo"
    assert data["stargazers_count"] == 10
    assert data["topics"] == ["cli"]
    assert data["license_spdx_id"] == "MIT"