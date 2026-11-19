# 🕶️ gh-finder

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MPL--2.0-green?style=flat-square)
![Status](https://img.shields.io/badge/status-MVP-orange?style=flat-square)
![GitHub Release](https://img.shields.io/github/v/release/del-Pacifico/gh-finder?display_name=tag)

**Search GitHub repositories from your terminal. Get readable results. Export to Markdown or JSON.**

`gh-finder` is a command-line tool that searches open-source repositories on GitHub using either guided flags or raw GitHub query syntax. It shows results in a clean table and can export them to Markdown or JSON with live links.

---

## Why gh-finder?

GitHub's official CLI (`gh`) is powerful, but its search output is minimal and its JSON export requires `jq` to be useful. `gh-finder` focuses on the experience of *discovering and documenting* repositories:

| Capability | `gh-finder` | `gh search repos` |
|---|---|---|
| Readable table by default (no flags) | ✅ | ❌ (requires `--json` + `jq`) |
| Markdown export with live links | ✅ `.md` | ❌ |
| Actionable message when token is missing | ✅ | N/A (always authenticated) |
| Guided query with flags | ✅ | ✅ |

`gh-finder` does not replace `gh`. It complements it when you need to document a search in Markdown without writing `jq`.

---

## Installation

### From PyPI (recommended)

    pip install gh-finder

### From the repository (development version)

    git clone https://github.com/del-Pacifico/gh-finder.git
    cd gh-finder
    pip install -e .

> **Note:** PyPI publication is planned. Until then, use the repository installation method.

---

## Quick Start

**Search by language:**

    gh-finder --language python

**Search with multiple filters:**

    gh-finder --language python --min-stars 500 --topic cli

**Use raw GitHub query syntax:**

    gh-finder --query "language:javascript stars:>=1000 topic:framework"

**Export results to Markdown:**

    gh-finder --language rust --min-stars 200 --output rust-repos.md

**Export results to JSON:**

    gh-finder --topic machine-learning --output ml-repos.json

---

## ⚡ Rate Limits

Without authentication, GitHub allows **60 requests per hour**.
With a `GITHUB_TOKEN`, the limit rises to **5,000 requests per hour**.

To create a token (no scopes needed for public repository search):

1. Go to https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Leave all scopes unchecked
4. Copy the token and set it as an environment variable:

**Windows (PowerShell):**

    $env:GITHUB_TOKEN = "ghp_..."

**macOS / Linux:**

    export GITHUB_TOKEN="ghp_..."

To check your current rate limit without consuming a search request:

    gh-finder --check-token

---

## Usage

`gh-finder` supports two mutually exclusive search modes:

- **Guided flags** (`--language`, `--min-stars`, `--topic`, `--in`, `--pushed-after`)
- **Raw query** (`--query`) for full GitHub search syntax

You cannot mix both modes in a single command.

### Common Flags

| Flag | Description |
|---|---|
| `--query "QUERY"` | Raw GitHub search syntax |
| `--language NAME` | Filter by programming language |
| `--min-stars N` | Minimum star count |
| `--topic NAME` | Filter by topic (can be repeated) |
| `--in FIELD` | Search in `name`, `description`, `readme`, or `topics` |
| `--pushed-after DATE` | Last push after `YYYY-MM-DD` |
| `--limit N` | Number of results (default: 10, max: 100) |
| `--output FILE` | Export to `.md` or `.json` |
| `--dry-run` | Show the generated query without calling the API |
| `--verbose` | Show HTTP request details |
| `--no-cache` | Bypass local cache |
| `--check-token` | Show remaining rate limit |

For the complete reference, including error handling and cache behavior, see [`docs/PROJECT_FRAMEWORK.md`](docs/PROJECT_FRAMEWORK.md).

---

## Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening an issue or pull request.

- Bug reports: use the `[Bug]` template
- Feature requests: use the `[Feature]` template
- Questions: use GitHub Discussions

This project follows the [Del-Pacifico Code of Conduct](CODE_OF_CONDUCT.md).

---

## License

Mozilla Public License 2.0. See [`LICENSE`](LICENSE) for details.

---

![GitHub Stars](https://img.shields.io/github/stars/del-Pacifico/gh-finder?style=flat-square&logo=github)
![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue?style=flat-square&logo=python)
![CLI](https://img.shields.io/badge/Interface-CLI-lightgrey?style=flat-square)
![Open Source](https://img.shields.io/badge/Open%20Source-Yes-brightgreen?style=flat-square&logo=github)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen?style=flat-square)
![Made with ❤️ by Del-Pacifico](https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F%20by%20Del--Pacifico-orange?style=flat-square)