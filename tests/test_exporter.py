# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/
#
# Original Author: Sergio Palma Hidalgo
# Project URL: https://github.com/del-Pacifico/gh-finder
# Copyright (c) 2025 Sergio Palma Hidalgo
# All rights reserved.
# test_exporter.py - gh-finder

"""Tests for gh_finder.exporter."""

import json

import pytest

from gh_finder.exporter import UnsupportedFormatError, export_results
from gh_finder.models import RepoResult


def _sample_results():
    return [
        RepoResult(
            full_name="owner/repo",
            html_url="https://github.com/owner/repo",
            description="A test repository",
            language="Python",
            stargazers_count=100,
            pushed_at="2025-01-01T00:00:00Z",
        )
    ]


def test_export_markdown(tmp_path):
    output = tmp_path / "results.md"
    export_results(_sample_results(), output)

    content = output.read_text(encoding="utf-8")
    assert "# gh-finder – Search Results" in content
    assert "[owner/repo](https://github.com/owner/repo)" in content
    assert "A test repository" in content
    assert "Python" in content
    assert "100" in content


def test_export_markdown_escapes_pipes(tmp_path):
    results = [
        RepoResult(
            full_name="owner/repo",
            html_url="https://github.com/owner/repo",
            description="Uses | pipes | inside",
        )
    ]
    output = tmp_path / "results.md"
    export_results(results, output)

    content = output.read_text(encoding="utf-8")
    assert "Uses \\| pipes \\| inside" in content


def test_export_markdown_truncates_long_description(tmp_path):
    results = [
        RepoResult(
            full_name="owner/repo",
            html_url="https://github.com/owner/repo",
            description="x" * 200,
        )
    ]
    output = tmp_path / "results.md"
    export_results(results, output)

    content = output.read_text(encoding="utf-8")
    assert "…" in content
    # The row must not contain a 200-character run.
    assert "x" * 200 not in content


def test_export_markdown_handles_newlines(tmp_path):
    results = [
        RepoResult(
            full_name="owner/repo",
            html_url="https://github.com/owner/repo",
            description="Line one\nLine two",
        )
    ]
    output = tmp_path / "results.md"
    export_results(results, output)

    content = output.read_text(encoding="utf-8")
    assert "Line one Line two" in content


def test_export_json(tmp_path):
    output = tmp_path / "results.json"
    export_results(_sample_results(), output)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["full_name"] == "owner/repo"
    assert data[0]["stargazers_count"] == 100


def test_export_unsupported_extension(tmp_path):
    output = tmp_path / "results.txt"
    with pytest.raises(UnsupportedFormatError, match="Unsupported output format"):
        export_results(_sample_results(), output)


def test_export_missing_extension(tmp_path):
    output = tmp_path / "results"
    with pytest.raises(UnsupportedFormatError, match="must have an extension"):
        export_results(_sample_results(), output)


def test_export_creates_non_empty_file(tmp_path):
    output = tmp_path / "results.json"
    export_results(_sample_results(), output)

    assert output.exists()
    assert output.stat().st_size > 0