# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/
#
# Original Author: Sergio Palma Hidalgo
# Project URL: https://github.com/del-Pacifico/gh-finder
# Copyright (c) 2025 Sergio Palma Hidalgo
# All rights reserved.
# models.py - gh-finder

"""Data models for gh-finder."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RepoResult:
    """Represents a single repository search result."""

    full_name: str
    html_url: str
    description: str | None = None
    language: str | None = None
    stargazers_count: int = 0
    pushed_at: str | None = None
    forks_count: int = 0
    open_issues_count: int = 0
    created_at: str | None = None
    topics: list[str] = field(default_factory=list)
    license_spdx_id: str | None = None

    @classmethod
    def from_api_payload(cls, payload: dict[str, Any]) -> RepoResult:
        """Map a GitHub API repository payload to a RepoResult instance.

        Missing or null fields are handled gracefully with sensible defaults.
        """
        license_info = payload.get("license") or {}

        return cls(
            full_name=payload.get("full_name", ""),
            html_url=payload.get("html_url", ""),
            description=payload.get("description"),
            language=payload.get("language"),
            stargazers_count=payload.get("stargazers_count", 0) or 0,
            pushed_at=payload.get("pushed_at"),
            forks_count=payload.get("forks_count", 0) or 0,
            open_issues_count=payload.get("open_issues_count", 0) or 0,
            created_at=payload.get("created_at"),
            topics=payload.get("topics", []) or [],
            license_spdx_id=license_info.get("spdx_id"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary representation."""
        return asdict(self)