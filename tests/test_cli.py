# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/
#
# Original Author: Sergio Palma Hidalgo
# Project URL: https://github.com/del-Pacifico/gh-finder
# Copyright (c) 2025 Sergio Palma Hidalgo
# All rights reserved.
# test_cli.py - gh-finder

"""Tests for gh_finder.cli."""

from unittest.mock import Mock, patch

from gh_finder.cli import _build_guided_query, _build_parser, main
from gh_finder.models import RepoResult


def _parse(argv):
    return _build_parser().parse_args(argv)


def test_guided_query_language():
    args = _parse(["--language", "python"])
    assert _build_guided_query(args) == "language:python"


def test_guided_query_multiple_flags():
    args = _parse(
        ["--language", "python", "--min-stars", "500", "--topic", "cli"]
    )
    assert _build_guided_query(args) == "language:python stars:>=500 topic:cli"


def test_guided_query_multiple_topics():
    args = _parse(["--topic", "bookmark", "--topic", "tabs"])
    assert _build_guided_query(args) == "topic:bookmark topic:tabs"


def test_query_and_guided_flags_are_mutually_exclusive(capsys):
    exit_code = main(["--query", "language:python", "--language", "python"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "--query cannot be combined with guided flags" in captured.err


def test_no_criteria_returns_error(capsys):
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "No search criteria provided" in captured.err


@patch("gh_finder.cli.search_repositories")
def test_dry_run_does_not_call_api(mock_search, capsys):
    exit_code = main(["--language", "python", "--dry-run"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Query: language:python" in captured.out
    mock_search.assert_not_called()


@patch("gh_finder.cli.search_repositories")
def test_limit_is_capped(mock_search, capsys):
    mock_search.return_value = []
    exit_code = main(["--language", "python", "--limit", "500"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "--limit capped at 100" in captured.err
    assert mock_search.call_args.kwargs["limit"] == 100


@patch("gh_finder.cli.search_repositories")
def test_search_success_prints_table(mock_search, capsys):
    mock_search.return_value = [
        RepoResult(
            full_name="owner/repo",
            html_url="https://github.com/owner/repo",
            description="Test repo",
            language="Python",
            stargazers_count=100,
            pushed_at="2025-01-01T00:00:00Z",
        )
    ]
    exit_code = main(["--language", "python"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "owner/repo" in captured.out
    assert "https://github.com/owner/repo" in captured.out


@patch("gh_finder.cli.search_repositories")
def test_output_unsupported_extension(mock_search, tmp_path, capsys):
    mock_search.return_value = []
    output = tmp_path / "results.txt"
    exit_code = main(["--language", "python", "--output", str(output)])
    captured = capsys.readouterr()
    assert exit_code == 8
    assert "Unsupported output format" in captured.err


@patch("gh_finder.cli.search_repositories")
def test_rate_limit_error_returns_code_3(mock_search, capsys):
    from gh_finder.github_client import RateLimitError

    mock_search.side_effect = RateLimitError("rate limited")
    exit_code = main(["--language", "python"])
    captured = capsys.readouterr()
    assert exit_code == 3
    assert "rate limited" in captured.err


@patch("gh_finder.cli.check_rate_limit")
def test_check_token(mock_check, capsys, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    mock_check.return_value = {"resources": {"search": {"remaining": 47, "limit": 60}}}
    exit_code = main(["--check-token"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "47/60" in captured.out


@patch("gh_finder.cli._start_spinner")
@patch("gh_finder.cli.search_repositories")
def test_spinner_is_started(mock_search, mock_spinner, capsys):
    mock_search.return_value = []
    stop_event = Mock()
    stop_event.set = Mock()
    thread = Mock()
    thread.join = Mock()
    mock_spinner.return_value = (stop_event, thread)

    exit_code = main(["--language", "python"])

    assert exit_code == 0
    mock_spinner.assert_called_once_with("Working...")
    stop_event.set.assert_called_once()
    thread.join.assert_called_once()

def test_query_with_guided_flags_returns_error(capsys):
    exit_code = main(["--query", "language:python", "--in", "name"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "--query cannot be combined with guided flags" in captured.err
    assert "--in" in captured.err