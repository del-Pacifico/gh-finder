# 🕶️ gh-finder – Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- Initial project structure with `gh_finder/` package (`cli`, `github_client`, `models`, `exporter`).
- `tests/` directory for pytest test suite.
- `docs/PROJECT_FRAMEWORK.md` with the complete MVP specification.
- GitHub issue templates: `bug_report.yml`, `feature_request.md`, `documentation.yml`, `question.yml`, `refactor.yml`, and `config.yml`.
- `PULL_REQUEST_TEMPLATE.md` adapted from Del-Pacifico conventions.
- Label taxonomy: `type:*`, `priority:*`, `status:*`, `needs:*`, `scope:*`.
- `README.md` with quick start, rate-limit guidance, and usage examples.
- `LICENSE` (Mozilla Public License 2.0) and `docs/LICENSE-SUMMARY.md`.
- `CONTRIBUTING.md` adapted for a Python CLI project.

---

## [0.1.0] - TBD

### Added

- Core search functionality via guided flags (`--language`, `--min-stars`, `--topic`, `--in`, `--pushed-after`).
- Raw query mode via `--query` (mutually exclusive with guided flags).
- Console output as a readable table.
- Markdown export via `--output *.md`.
- JSON export via `--output *.json`.
- Optional authentication via `GITHUB_TOKEN`.
- Actionable error messages for rate limits, invalid queries, and server errors.
- Local cache with 5-minute TTL and `--no-cache` override.
- `--dry-run`, `--verbose`, and `--check-token` flags.

[Unreleased]: https://github.com/del-Pacifico/gh-finder/compare/main...HEAD
[0.1.0]: https://github.com/del-Pacifico/gh-finder/releases/tag/v0.1.0
