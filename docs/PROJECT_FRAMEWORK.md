# 🕶️ gh-finder – Project Framework

> **Status:** MVP definition complete. Ready for implementation.

---

## 📋 Table of Contents

- [🕶️ gh-finder – Project Framework](#️-gh-finder--project-framework)
  - [📋 Table of Contents](#-table-of-contents)
  - [1. Project Overview](#1-project-overview)
  - [2. Scope: MVP vs. Post-MVP](#2-scope-mvp-vs-post-mvp)
  - [3. Architecture](#3-architecture)
  - [4. CLI Interface](#4-cli-interface)
    - [Search Modes (mutually exclusive)](#search-modes-mutually-exclusive)
    - [Additional Flags](#additional-flags)
  - [5. Usage Examples](#5-usage-examples)
    - [Basic Usage](#basic-usage)
    - [Intermediate Usage](#intermediate-usage)
    - [Advanced Usage](#advanced-usage)
    - [Incorrect Usage (and Why)](#incorrect-usage-and-why)
    - [What Each Example Teaches](#what-each-example-teaches)
  - [6. Flag → GitHub Qualifier Mapping](#6-flag--github-qualifier-mapping)
  - [7. Output Behavior](#7-output-behavior)
    - [Console (default)](#console-default)
    - [Export (`--output`)](#export---output)
  - [8. Error Handling](#8-error-handling)
  - [9. Cache Strategy](#9-cache-strategy)
  - [10. Logging \& Language Rules](#10-logging--language-rules)
  - [11. Testing Strategy](#11-testing-strategy)
    - [Layer 1: Argument Parser (`test_cli.py`)](#layer-1-argument-parser-test_clipy)
    - [Layer 2: Query Assembly \& HTTP Client (`test_github_client.py`)](#layer-2-query-assembly--http-client-test_github_clientpy)
    - [Layer 3: Exporters (`test_exporter.py`)](#layer-3-exporters-test_exporterpy)
  - [12. Repository Structure](#12-repository-structure)
  - [13. Differentiation from `gh search repos`](#13-differentiation-from-gh-search-repos)
  - [14. Known Limitations](#14-known-limitations)
  - [15. Rate Limits \& Authentication](#15-rate-limits--authentication)
    - [Prominent README section](#prominent-readme-section)
    - [`--check-token` behavior](#--check-token-behavior)
  - [16. Validation \& Definition of Done](#16-validation--definition-of-done)

---

## 1. Project Overview

**gh-finder** is a command-line application for searching open-source repositories on GitHub using either raw GitHub query syntax (`--query`) or guided flags (`--language`, `--min-stars`, `--topic`, etc.). It returns a readable table by default and optionally exports results to Markdown or JSON with live links.

- **Organization:** [Del-Pacifico](https://github.com/del-Pacifico)
- **License:** Mozilla Public License 2.0 (MPL 2.0)
- **Language:** Python 3.10+
- **Packaging:** `pyproject.toml` with installable entry point (`gh-finder`)
- **Status:** MVP — focused on core search and export. Additional formats and features are post-MVP.

---

## 2. Scope: MVP vs. Post-MVP

| Component | MVP | Post-MVP |
|---|---|---|
| Search modes | `--query` OR guided flags (mutually exclusive) | Interactive guided mode |
| Console output | Table with 6 fields | — |
| Export | `.md` and `.json` (inferred by extension) | `.docx`, `.csv` |
| Token | Optional via `GITHUB_TOKEN`; actionable message if absent | — |
| Cache | JSON on disk, TTL 5 min, `--no-cache` | — |
| Debug | `--dry-run`, `--verbose`, `--check-token` | — |
| Tests | pytest: parser, mocked client, exporters | — |
| Errors | 403 primary/secondary, 422, 5xx, timeout with specific messages | — |
| Docs | README with prominent rate-limit section, clear `--help` | — |

> ⚠️ **Note:** This is the MVP. It will migrate to all other options in subsequent iterations. The MVP is intentionally narrow to reduce surface area for bugs and to ship a usable tool quickly.

---

## 3. Architecture

    gh-finder/
    ├── gh_finder/
    │   ├── __init__.py
    │   ├── cli.py              # Argument parsing, orchestration
    │   ├── github_client.py    # API call, token/rate limit handling
    │   ├── models.py           # RepoResult dataclass
    │   └── exporter.py         # Markdown and JSON export
    ├── tests/
    │   ├── test_cli.py
    │   ├── test_github_client.py
    │   └── test_exporter.py
    └── pyproject.toml

**Principles:**

- 1 file = 1 concern (per Del-Pacifico `CONTRIBUTING.md`)
- No external libraries beyond `requests` and `platformdirs`
- No database, no persistent state beyond cache
- All errors caught and translated to actionable messages; no raw tracebacks

---

## 4. CLI Interface

    gh-finder [--query "QUERY"] [GUIDED FLAGS] [--limit N] [--output FILE] [--dry-run] [--verbose] [--no-cache] [--check-token]

### Search Modes (mutually exclusive)

**Mode A — Raw query:**

    gh-finder --query "language:python stars:>=500 topic:cli"

**Mode B — Guided flags:**

    gh-finder --language python --min-stars 500 --topic cli

> ⚠️ **Using `--query` together with any guided flag is an error.** The `--help` output must state this explicitly:
>
> `"Use --query for raw GitHub syntax, OR use --language, --min-stars, etc. for guided mode. Do not mix."`

### Additional Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--limit` | integer | 10 | Number of results (1–100). Capped at 100 with warning. |
| `--output` | path | — | Export file. Format inferred from `.md` or `.json` extension. |
| `--dry-run` | flag | off | Print the generated query and URL without calling the API. |
| `--verbose` | flag | off | Show HTTP request details (URL, status, response time). |
| `--no-cache` | flag | off | Bypass local cache and force a fresh API request. |
| `--check-token` | flag | off | Query `GET /rate_limit` and display remaining requests. |

---

## 5. Usage Examples

### Basic Usage

**Search by language only:**

    gh-finder --language python

**Search by topic only:**

    gh-finder --topic bookmark

**Raw query with a simple filter:**

    gh-finder --query "language:javascript stars:>=1000"

**Export the last search to Markdown:**

    gh-finder --language python --output results.md

**Check remaining rate limit without consuming search quota:**

    gh-finder --check-token

---

### Intermediate Usage

**Combine multiple guided flags (AND semantics):**

    gh-finder --language python --min-stars 500 --topic cli

**Multiple topics in a single search:**

    gh-finder --topic bookmark --topic tabs --topic browser

**Limit results and export to JSON:**

    gh-finder --language rust --min-stars 1000 --limit 25 --output rust-repos.json

**Filter by last push date:**

    gh-finder --language go --pushed-after 2024-01-01 --min-stars 100

**Restrict search to repository name only:**

    gh-finder --in name --query "cli"

**Preview the generated query without calling the API:**

    gh-finder --language python --min-stars 500 --dry-run

Expected output:

    Query: language:python stars:>=500
    URL:   https://api.github.com/search/repositories?q=language%3Apython+stars%3A%3E%3D500&per_page=10

---

### Advanced Usage

**Raw query with multiple qualifiers and a specific limit:**

    gh-finder --query "language:python topic:cli archived:false forks:>100" --limit 50

**Export a large result set to Markdown for a report:**

    gh-finder --query "topic:machine-learning stars:>=2000 pushed:>2024-06-01" --limit 100 --output ml-repos.md

**Force a fresh API request, bypassing cache:**

    gh-finder --language python --no-cache

**Verbose mode for debugging API behavior:**

    gh-finder --query "language:rust" --verbose

Expected output includes:

    [gh-finder] GET https://api.github.com/search/repositories?q=language%3Arust&per_page=10
    [gh-finder] Status: 200 | Time: 0.42s | Remaining: 58/60

**Combine `--dry-run` with `--query` to learn GitHub syntax without spending requests:**

    gh-finder --query "language:typescript stars:>=5000 topic:framework" --dry-run

**Use a token for higher limits and export results:**

    export GITHUB_TOKEN=ghp_...
    gh-finder --language python --min-stars 1000 --limit 100 --output python-repos.md

---

### Incorrect Usage (and Why)

| Command | Why it fails | Correct alternative |
|---|---|---|
| `gh-finder --query "language:python" --language python` | `--query` and guided flags are mutually exclusive. | Use one mode only: `gh-finder --query "language:python"` or `gh-finder --language python`. |
| `gh-finder` | No search criteria provided. | `gh-finder --language python` or `gh-finder --query "stars:>=100"`. |
| `gh-finder --output results.txt` | Unsupported extension. | `gh-finder --output results.md` or `gh-finder --output results.json`. |
| `gh-finder --output results` | No extension, format cannot be inferred. | `gh-finder --output results.md`. |
| `gh-finder --limit 500` | Exceeds API per-page limit. | Capped at 100 with a warning; use `--limit 100` explicitly. |
| `gh-finder --language` | Missing value for flag. | `gh-finder --language python`. |
| `gh-finder --min-stars abc` | Non-integer value. | `gh-finder --min-stars 100`. |
| `gh-finder --in stars` | `--in` only accepts `name`, `description`, `readme`, `topics`. | `gh-finder --in name --query "cli"`. |
| `gh-finder --query "language:python" --dry-run --output results.md` | `--dry-run` does not call the API, so no results to export. | Remove `--output` when using `--dry-run`. |

---

### What Each Example Teaches

| Example | Concept |
|---|---|
| `gh-finder --language python` | Minimal guided search |
| `gh-finder --query "..."` | Raw GitHub syntax escape hatch |
| `--topic a --topic b` | Multiple values with AND semantics |
| `--dry-run` | Query preview without API cost |
| `--check-token` | Rate limit visibility |
| `--verbose` | HTTP debugging |
| `--no-cache` | Cache bypass |
| `--output results.md` | Export format inference |
| `--limit 100` | Maximum per-page results |
| `export GITHUB_TOKEN=...` | Authentication for higher limits |

---

## 6. Flag → GitHub Qualifier Mapping

| gh-finder Flag | Generated Qualifier | Notes |
|---|---|---|
| `--language python` | `language:python` | Single value. Multiple occurrences → error. |
| `--min-stars 500` | `stars:>=500` | Positive integer. |
| `--topic bookmark` | `topic:bookmark` | `action='append'` for multiple values. Each generates a separate qualifier. |
| `--in name` | `in:name` | Allowed: `name`, `description`, `readme`, `topics`. Validated against closed list. |
| `--pushed-after 2024-01-01` | `pushed:>2024-01-01` | Validated as `YYYY-MM-DD`. |

**Assembly:** qualifiers are joined with spaces. Multiple `--topic` values produce `topic:a topic:b` (AND semantics).

**No criteria provided:** error with example:

    No search criteria provided. Try:
      gh-finder --language python --min-stars 100
      gh-finder --query "topic:cli stars:>=500"

---

## 7. Output Behavior

### Console (default)

Table with 6 fields:

| Field | Justification |
|---|---|
| `full_name` | Human-readable identifier (`owner/repo`) |
| `html_url` | Direct URL to repository |
| `description` | The "About" field for context |
| `language` | Technical context |
| `stargazers_count` | Relevance/popularity signal |
| `pushed_at` | Activity indicator |

Description truncated to ~60 chars with `…` if longer. Columns aligned, no colors.

### Export (`--output`)

Format inferred by extension:

- `resultados.md` → Markdown table with live links
- `resultados.json` → JSON array with all `RepoResult` fields

Unsupported extension → error:

    Unsupported output format: .txt. Supported formats: .md, .json.

No extension → error requesting explicit `.md` or `.json`.

---

## 8. Error Handling

| Scenario | Message |
|---|---|
| 403 with `X-RateLimit-Remaining: 0` | `"GitHub rate limit exceeded. You have {remaining} requests left until {reset_time}. Set the GITHUB_TOKEN environment variable to increase your limit from 60 to 5,000 requests/hour."` |
| 403 with `Retry-After` header | `"GitHub secondary rate limit triggered. Wait {seconds} seconds and try again."` |
| 403 without headers | `"GitHub returned 403. This may be a rate limit or a secondary limit triggered by rapid requests. Wait a moment and try again."` |
| 422 | `"GitHub rejected the search query: {message}. Check your syntax or run with --dry-run to see the generated query."` |
| 500, 502, 503 | `"GitHub returned a server error ({status}). This is not a problem with gh-finder. Try again in a few minutes."` |
| Timeout / connection failure | `"Could not reach GitHub. Check your network connection and try again."` |

**Rule:** no raw Python tracebacks visible to the user. All exceptions caught, logged at debug level (if `--verbose`), and translated to actionable messages.

**Encapsulation:** all 403 logic lives in `_handle_403(response)`. The main flow only calls it; never inspects headers directly.

---

## 9. Cache Strategy

- **Location:** `~/.cache/gh-finder/` (resolved via `platformdirs`)
- **Key:** hash of query + `per_page` + token presence
- **Format:** one JSON file per entry (`{hash}.json`) containing timestamp and payload
- **TTL:** 5 minutes. Expired entries ignored and lazily deleted.
- **Control:** `--no-cache` forces fresh request.
- **Log when cache is used:**

    [gh-finder] Using cached results (age: 2m 15s). Use --no-cache to force a fresh request.

No Redis, no SQLite. Volume is minimal.

---

## 10. Logging & Language Rules

| Rule | Implementation |
|---|---|
| Log prefix | `[gh-finder]: message` |
| No emoji in error logs | Optional in info messages |
| Use `logging.debug()` / `logging.info()` | Controlled by `--verbose` |
| No console-only errors | All API errors caught and translated |
| No crashes from logic failures | `try/except` around HTTP call and response parsing; traceback only with `--verbose` |
| Language | American English in comments, docstrings, CLI messages, README, CHANGELOG |
| Tone | Professional, objective, approachable |

---

## 11. Testing Strategy

### Layer 1: Argument Parser (`test_cli.py`)

- `--query` + guided flags → error
- `--query` alone → raw query built, no qualifier assembly
- `--language python --min-stars 100` → correct query assembly
- Multiple `--topic` → multiple qualifiers
- No search arguments → error with expected message
- `--output file.txt` → unsupported format error
- `--limit 500` → capped at 100 with warning

### Layer 2: Query Assembly & HTTP Client (`test_github_client.py`)

- Mock `requests.get`. Verify constructed URL is correct.
- Simulate 200 with sample payload → `RepoResult` populated correctly
- Simulate 403 (primary), 403 (secondary with `Retry-After`), 422, 500 → specific exceptions raised
- `--dry-run` does not call `requests.get`
- `--check-token` calls `GET /rate_limit`, not search endpoint

### Layer 3: Exporters (`test_exporter.py`)

- Markdown: contains headers, rows with links, escapes pipes in descriptions (critical for tables)
- JSON: valid structure, expected fields present
- Generated file exists and has non-empty content

**Execution:** `pytest` + `ruff check .`. Both must pass before commit (per Del-Pacifico `CONTRIBUTING.md`).

---

## 12. Repository Structure

    gh-finder/
    ├── .github/
    │   ├── ISSUE_TEMPLATE/
    │   │   ├── bug_report.yml
    │   │   └── feature_request.yml
    │   ├── workflows/
    │   │   └── ci.yml
    │   └── PULL_REQUEST_TEMPLATE.md
    ├── docs/
    │   ├── philosophy.md
    │   └── roadmap.md
    ├── gh_finder/
    │   ├── __init__.py
    │   ├── cli.py
    │   ├── github_client.py
    │   ├── models.py
    │   └── exporter.py
    ├── tests/
    │   ├── test_cli.py
    │   ├── test_github_client.py
    │   └── test_exporter.py
    ├── .gitignore
    ├── CHANGELOG.md
    ├── CODE_OF_CONDUCT.md
    ├── CONTRIBUTING.md
    ├── LICENSE
    ├── README.md
    ├── SECURITY.md
    ├── pyproject.toml
    └── VERSION

**Adapted from Del-Pacifico conventions:**

- Commit format: `feat(cli): add --query exclusive mode (#12)`
- Branch naming: `feature/12-query-flag`
- MPL 2.0 license header in every `.py` file
- Local validation before commit: `ruff check .` + `pytest`

---

## 13. Differentiation from `gh search repos`

`gh-finder` does not replace `gh`. It complements it when you need to document a search in Markdown without writing `jq`.

| Capability | `gh-finder` | `gh search repos` | `curl` + `jq` |
|---|---|---|---|
| Readable table by default (no flags) | ✅ | ❌ (requires `--json` + `jq`) | ❌ |
| Markdown export with live links | ✅ `.md` | ❌ | ❌ |
| Actionable message when token is missing | ✅ | N/A (always authenticated) | ❌ |
| Guided query with flags | ✅ | ✅ | ❌ |

**README opening line:**

> `gh-finder` does not replace `gh`. It complements it when you need to document a search in Markdown without writing `jq`.

---

## 14. Known Limitations

- **GitHub API search results are capped at 1,000 total.** No matter how many pages are requested, page 11 onward returns a 422 error: `"Only the first 1000 search results are available"`. The MVP caps `--limit` at 100, so this is documented but not hit in practice.
- **`--limit` is capped at 100.** Values above 100 trigger a warning and are silently capped.
- **DOCX and CSV are not in the MVP.** They are post-MVP iterations.
- **Interactive mode is not in the MVP.** It is a post-MVP feature for new users.

---

## 15. Rate Limits & Authentication

### Prominent README section

The README must include a visible section (not a footnote) with the following content:

    ## ⚡ Rate Limits

    Without authentication, GitHub allows 60 requests per hour.
    With a GITHUB_TOKEN, the limit rises to 5,000 requests per hour.

    To create a token (no scopes needed for public repo search):
    1. Go to https://github.com/settings/tokens
    2. Click "Generate new token (classic)"
    3. Leave all scopes unchecked
    4. Copy the token and export it:
       export GITHUB_TOKEN=ghp_...

### `--check-token` behavior

Calls `GET /rate_limit` (does not consume search quota) and displays:

    [gh-finder] No GITHUB_TOKEN found. Remaining requests: 47/60 this hour.
    [gh-finder] To increase your limit to 5,000/hour, see: https://github.com/settings/tokens

---

## 16. Validation & Definition of Done

An Issue or PR is **ready for review** when:

- [ ] Change is scoped to a single confirmed defect or approved feature
- [ ] `ruff check .` and `pytest` pass locally
- [ ] `CHANGELOG.md` entry drafted (for user-facing changes)
- [ ] Documentation updated if behavior, flags, or output changed
- [ ] PR description includes: linked Issue, summary, affected modules, QA evidence (logs or screenshots)
- [ ] No unrelated refactors or "while I'm here" changes mixed in
- [ ] AI assistance disclosed in PR description (if applicable)

---

*End of project framework. Ready for implementation.*