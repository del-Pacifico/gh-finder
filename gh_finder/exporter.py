# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/
#
# Original Author: Sergio Palma Hidalgo
# Project URL: https://github.com/del-Pacifico/gh-finder
# Copyright (c) 2025 Sergio Palma Hidalgo
# All rights reserved.
# exporter.py - gh-finder

"""Export search results to Markdown or JSON."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from gh_finder.models import RepoResult

logger = logging.getLogger(__name__)

MARKDOWN_DESCRIPTION_LIMIT = 60
SUPPORTED_EXTENSIONS = {".md": "_export_markdown", ".json": "_export_json"}


class UnsupportedFormatError(Exception):
    """Raised when the output file extension is not supported."""


def _truncate(text: str, limit: int = MARKDOWN_DESCRIPTION_LIMIT) -> str:
    """Truncate text to the given limit, appending an ellipsis if needed."""
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _escape_markdown_cell(text: str) -> str:
    """Escape characters that would break a Markdown table cell."""
    # Pipes break the table structure; newlines break the row.
    return text.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def _export_markdown(results: list[RepoResult], path: Path) -> None:
    """Write results to a Markdown table with live links."""
    lines = [
        "# gh-finder – Search Results",
        "",
        "| Repository | URL | Description | Language | Stars | Last Push |",
        "|---|---|---|---|---|---|",
    ]
    for repo in results:
        description = _escape_markdown_cell(repo.description or "")
        description = _truncate(description)
        name = f"[{repo.full_name}]({repo.html_url})"
        stars = str(repo.stargazers_count)
        language = repo.language or "—"
        pushed = repo.pushed_at or "—"
        lines.append(
            f"| {name} | {repo.html_url} | {description} | {language} | {stars} | {pushed} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("[gh-finder] Exported %d results to %s (Markdown)", len(results), path)


def _export_json(results: list[RepoResult], path: Path) -> None:
    """Write results to a JSON array."""
    data = [repo.to_dict() for repo in results]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("[gh-finder] Exported %d results to %s (JSON)", len(results), path)


def export_results(results: list[RepoResult], output_path: Path) -> None:
    """Export results to the format inferred from the output file extension.

    Raises UnsupportedFormatError if the extension is missing or not supported.
    """
    extension = output_path.suffix.lower()
    if not extension:
        raise UnsupportedFormatError(
            "Output file must have an extension (.md or .json). "
            f"Received: {output_path.name}"
        )
    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFormatError(
            f"Unsupported output format: {extension}. Supported formats: .md, .json."
        )

    exporter = globals()[SUPPORTED_EXTENSIONS[extension]]
    exporter(results, output_path)