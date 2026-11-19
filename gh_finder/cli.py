# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/
#
# Original Author: Sergio Palma Hidalgo
# Project URL: https://github.com/del-Pacifico/gh-finder
# Copyright (c) 2025 Sergio Palma Hidalgo
# All rights reserved.
# cli.py - gh-finder

"""Command-line interface for gh-finder."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from gh_finder.exporter import UnsupportedFormatError, export_results
from gh_finder.github_client import (
    GitHubClientError,
    NetworkError,
    QueryError,
    RateLimitError,
    ServerError,
    check_rate_limit,
    search_repositories,
)
from gh_finder.models import RepoResult

logger = logging.getLogger(__name__)

MAX_LIMIT = 100
DEFAULT_LIMIT = 10
DESCRIPTION_MAX_WIDTH = 60


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with mutually exclusive search modes."""
    parser = argparse.ArgumentParser(
        prog="gh-finder",
        description="Search GitHub repositories and export results to Markdown or JSON.",
        epilog=(
            "Use --query for raw GitHub syntax, OR use --language, --min-stars, "
            "etc. for guided mode. Do not mix."
        ),
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--query",
        metavar="QUERY",
        help="Raw GitHub search query (e.g., 'language:python stars:>=500').",
    )

    mode.add_argument(
        "--language",
        metavar="NAME",
        help="Filter by programming language (e.g., python).",
    )

    parser.add_argument(
        "--min-stars",
        type=int,
        metavar="N",
        help="Minimum number of stars (translated to stars:>=N).",
    )
    parser.add_argument(
        "--topic",
        action="append",
        metavar="NAME",
        help="Filter by topic. Repeat the flag for multiple topics.",
    )
    parser.add_argument(
        "--in",
        dest="in_field",
        choices=["name", "description", "readme", "topics"],
        metavar="FIELD",
        help="Search in name, description, readme, or topics.",
    )
    parser.add_argument(
        "--pushed-after",
        metavar="YYYY-MM-DD",
        help="Filter by last push date (translated to pushed:>DATE).",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        metavar="N",
        help=f"Number of results (default: {DEFAULT_LIMIT}, max: {MAX_LIMIT}).",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Export results to .md or .json (format inferred by extension).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated query without calling the API.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show HTTP request details.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass local cache and force a fresh API request.",
    )
    parser.add_argument(
        "--check-token",
        action="store_true",
        help="Show remaining rate limit without consuming search quota.",
    )

    return parser


def _build_guided_query(args: argparse.Namespace) -> str:
    """Assemble a GitHub query string from guided flags."""
    parts: list[str] = []
    if args.language:
        parts.append(f"language:{args.language}")
    if args.min_stars is not None:
        parts.append(f"stars:>={args.min_stars}")
    if args.topic:
        parts.extend(f"topic:{topic}" for topic in args.topic)
    if args.in_field:
        parts.append(f"in:{args.in_field}")
    if args.pushed_after:
        parts.append(f"pushed:>{args.pushed_after}")
    return " ".join(parts)


def _resolve_query(args: argparse.Namespace) -> str:
    """Resolve the final query from --query or guided flags."""
    if args.query:
        return args.query

    guided = _build_guided_query(args)
    if not guided:
        raise ValueError(
            "No search criteria provided. Try:\n"
            "  gh-finder --language python --min-stars 100\n"
            "  gh-finder --query \"topic:cli stars:>=500\""
        )
    return guided


def _cap_limit(limit: int) -> int:
    """Cap the limit to the GitHub API maximum per page."""
    if limit < 1:
        raise ValueError(f"Invalid --limit: {limit}. Must be >= 1.")
    if limit > MAX_LIMIT:
        print(
            f"[gh-finder] --limit capped at {MAX_LIMIT} "
            f"(GitHub API maximum per page).",
            file=sys.stderr,
        )
        return MAX_LIMIT
    return limit


def _print_table(results: list[RepoResult]) -> None:
    """Print results as a readable table to stdout."""
    if not results:
        print("[gh-finder] No results found.")
        return

    for repo in results:
        description = (repo.description or "").replace("\n", " ")
        if len(description) > DESCRIPTION_MAX_WIDTH:
            description = description[: DESCRIPTION_MAX_WIDTH - 1].rstrip() + "…"

        print(f"{repo.full_name}")
        print(f"  URL:     {repo.html_url}")
        print(f"  About:   {description or '—'}")
        print(f"  Lang:    {repo.language or '—'}")
        print(f"  Stars:   {repo.stargazers_count}")
        print(f"  Pushed:  {repo.pushed_at or '—'}")
        print()


def _handle_check_token(token: str | None) -> int:
    """Query /rate_limit and print remaining requests."""
    try:
        data = check_rate_limit(token)
    except GitHubClientError as exc:
        print(f"[gh-finder] {exc}", file=sys.stderr)
        return 1

    search = data.get("resources", {}).get("search", {})
    remaining = search.get("remaining", "?")
    limit = search.get("limit", "?")
    if token:
        print(f"[gh-finder] GITHUB_TOKEN detected. Remaining search requests: {remaining}/{limit}.")
    else:
        print(f"[gh-finder] No GITHUB_TOKEN found. Remaining requests: {remaining}/{limit} this hour.")
        print("[gh-finder] To increase your limit to 5,000/hour, see: https://github.com/settings/tokens")
    return 0


def _handle_dry_run(query: str, limit: int) -> int:
    """Print the query and URL without calling the API."""
    encoded = query.replace(" ", "+").replace(":", "%3A").replace(">", "%3E").replace("=", "%3D")
    url = f"https://api.github.com/search/repositories?q={encoded}&per_page={limit}"
    print(f"Query: {query}")
    print(f"URL:   {url}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point for the gh-finder CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    token = os.environ.get("GITHUB_TOKEN")

    if args.check_token:
        return _handle_check_token(token)

    try:
        query = _resolve_query(args)
    except ValueError as exc:
        print(f"[gh-finder] {exc}", file=sys.stderr)
        return 2

    try:
        limit = _cap_limit(args.limit)
    except ValueError as exc:
        print(f"[gh-finder] {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        return _handle_dry_run(query, limit)

    try:
        results = search_repositories(
            query=query,
            limit=limit,
            token=token,
            use_cache=not args.no_cache,
            verbose=args.verbose,
        )
    except RateLimitError as exc:
        print(f"[gh-finder] {exc}", file=sys.stderr)
        return 3
    except QueryError as exc:
        print(f"[gh-finder] {exc}", file=sys.stderr)
        return 4
    except ServerError as exc:
        print(f"[gh-finder] {exc}", file=sys.stderr)
        return 5
    except NetworkError as exc:
        print(f"[gh-finder] {exc}", file=sys.stderr)
        return 6
    except GitHubClientError as exc:
        print(f"[gh-finder] {exc}", file=sys.stderr)
        return 7

    _print_table(results)

    if args.output:
        try:
            export_results(results, Path(args.output))
        except UnsupportedFormatError as exc:
            print(f"[gh-finder] {exc}", file=sys.stderr)
            return 8

    return 0


if __name__ == "__main__":
    sys.exit(main())