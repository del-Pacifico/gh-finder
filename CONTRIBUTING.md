# 🕶️ gh-finder – Contributing Guide

Thank you for your interest in contributing to **gh-finder**! This guide provides everything you need to know to start contributing effectively and collaboratively.

> ⚠️ **Note:** This project operates under a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

---

## 📋 Quick Navigation

- [🏁 Getting Started](#-getting-started)
- [🤝 How to Contribute](#-how-to-contribute)
- [📝 Reporting & Proposing](#-reporting--proposing)
- [⚙️ Development Workflow](#️-development-workflow)
- [💻 Code & Documentation Standards](#-code--documentation-standards)
- [✅ Validation & Support](#-validation--support)

---

## 🏁 Getting Started

### ✅ Pre-requisites

Before you start contributing, make sure you have:

- **Python 3.10+** installed.
- **pip** (comes with Python).
- **Git** installed and configured.
- Basic familiarity with command-line tools and Python packaging.

### 💻 Development Environment Setup

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:

    git clone git@github.com:<your-user>/gh-finder.git
    cd gh-finder

3. **Add the upstream repository**:

    git remote add upstream git@github.com:del-Pacifico/gh-finder.git
    git fetch upstream

4. **Create a virtual environment** (recommended):

    python -m venv .venv

    # Windows:
    .venv\Scripts\activate

    # macOS/Linux:
    source .venv/bin/activate

5. **Install in editable mode with development dependencies**:

    pip install -e ".[dev]"

### 🎯 Project Principles

gh-finder is guided by principles that shape every decision:

1. **Minimal Technical Footprint** — Solve the actual problem. No over-engineering.
2. **Actionable Errors** — Every error message should tell the user what to do next.
3. **Readable Output by Default** — A clean table, no flags required.
4. **Export-Focused** — Markdown and JSON are first-class outputs.
5. **Optional Authentication** — Works without a token, better with one.

📖 Read the full framework in [`docs/PROJECT_FRAMEWORK.md`](docs/PROJECT_FRAMEWORK.md).

### 🗂️ Repository Structure

    gh-finder/
    ├── .github/           # Issue templates, PR template, workflows
    ├── docs/              # Project documentation
    ├── gh_finder/         # Core package
    │   ├── cli.py         # Argument parsing, orchestration
    │   ├── github_client.py # API calls, rate limits, cache
    │   ├── models.py      # RepoResult dataclass
    │   └── exporter.py    # Markdown and JSON export
    ├── tests/             # pytest tests
    ├── pyproject.toml     # Package metadata and tool config
    ├── README.md          # Project overview
    └── CONTRIBUTING.md    # This file

**Key rule:** Keep modules focused — 1 file = 1 concern.

### 👥 Team Roles

| Role | GitHub Handle | Responsibility |
|---|---|---|
| **Founder & Maintainer** | `sergiopalmah` | Project direction, final PR approval, merges to `main`, release management. |
| **Senior Collaborator** | `agentsmid` | Code implementation, local QA, atomic commits and pushes. |
| **Community Contributors** | You! | Bug reports, feature proposals, documentation improvements, code via PR. |

*All contributions are reviewed manually. There are no automatic approvals.*

---

## 🤝 How to Contribute

### 📌 Common Contribution Scenarios

- **"I want to report a bug"** → Use the `[Bug]` issue template.
- **"I want to suggest a feature"** → Open a GitHub Discussion first, then a `[Feature]` issue when scoped.
- **"I want to fix a typo or docs"** → Create a `docs/*` PR directly to `main`.
- **"I have a question"** → Use GitHub Discussions or the `[Question]` issue template.

### Choose the Right Channel

- **Use Discussions for:** Early ideas, open questions, design exploration, or support conversations.
- **Use Issues for:** Actionable bugs (confirmed and reproducible), approved feature requests, documentation problems.
- **Use Pull Requests only for:** Focused changes linked to an existing Issue or approved Discussion. PRs without a linked Issue/Discussion may be closed.

---

## 📝 Reporting & Proposing

### 🌟 Suggest a Feature

1. Describe the `problem` or `workflow gap`.
2. Explain `who benefits` and in `which scenarios`.
3. Describe the `expected behavior` from a user perspective.
4. Identify the `affected module` (`models`, `client`, `exporter`, `cli`, `cache`).
5. Note any `constraints` or `trade-offs`.
6. Open a GitHub Discussion first, then an Issue when actionable.

### 🐛 Report a Bug

1. Confirm you are using the latest `gh-finder` version.
2. Reproduce the behavior with a clean, minimal command.
3. Capture the environment: Python version, OS, gh-finder version.
4. Include the exact command you ran.
5. Collect evidence: expected vs. actual behavior, logs filtered by `[gh-finder]`.
6. Open a `[Bug]` issue. *Use one issue per defect.*

#### 📝 Example: Good vs. Bad Bug Report

**✅ Good Issue:**

    [Bug] --topic with multiple values produces duplicate qualifiers
    Command: gh-finder --topic bookmark --topic tabs --topic browser
    Python: 3.12.1
    OS: Windows 11
    gh-finder: 0.1.0
    Expected: topic:bookmark topic:tabs topic:browser
    Actual: topic:bookmark topic:bookmark topic:tabs topic:tabs topic:browser
    Logs: [gh-finder] Query assembled: topic:bookmark topic:bookmark topic:tabs topic:tabs topic:browser

**❌ Bad Issue:**

    [Bug] topics are broken
    It doesn't work. Please fix.

*Why it's bad: No command, no version, no logs, no expected behavior. Cannot be triaged.*

### 🔐 Security Vulnerability Reporting

If you discover a security vulnerability, **do not open a public issue**. Report it privately via [GitHub Security Advisories](https://github.com/del-Pacifico/gh-finder/security/advisories/new) or contact the maintainer directly.

---

## ⚙️ Development Workflow

**MVP phase:** `feature/fix/chore branch` → `main`

**Post-MVP:** `feature/fix/chore branch` → `dev` → `main` → `tag/release`

### 🌿 Branch and Commit Conventions

**Branch Naming:** `<type>/<issue-number>-<short-description>`

- Types: `feature`, `fix`, `docs`, `chore`, `refactor`, `test`
- Example: `fix/12-duplicate-topic-qualifiers`

**Commit Messages:** Follow Conventional Commits.

- Format: `<type>(<scope>): <description> (#<issue-number>)`
- Example: `fix(cli): prevent duplicate topic qualifiers (#12)`
- Rules: Present tense, imperative mood, no capitalization at start, no period at end.

#### 📝 Example: Good vs. Bad Commit

**✅ Good commit:**

    fix(cli): prevent duplicate topic qualifiers (#12)

**❌ Bad commit:**

    fixed stuff

> *Why it matters: Conventional Commits enable clean `git log`, automated changelogs, and fast triage.*

### 🥷🏼 Incremental Commit and Push Discipline

During active development, **each validated atomic change** must be committed and pushed to the current working branch as soon as it is complete.

- Keep the change scoped to the active issue/PR objective.
- Stage **only** the files that belong to the completed atomic change.
- Run local validation (`ruff check .`, `pytest`) before committing.
- Push immediately. *Do not batch unrelated changes into a single commit.*

### 🏷️ Issue Title Prefixes & Labeling Rules

**Title Prefixes:** `[Bug]`, `[Feature]`, `[Docs]`, `[Refactor]`, `[Question]`.

#### Label Taxonomy:

- **Work type:** `type: bug`, `type: feature`, `type: documentation`, `type: chore`, `type: refactor`, `type: question`
- **Affected module:** `scope: models`, `scope: client`, `scope: exporter`, `scope: cli`, `scope: cache`, `scope: docs`
- **Priority/Lifecycle:** `priority: high`, `priority: normal`, `priority: low`, `status: backlog`, `status: in-progress`, `needs: triage`, `needs: reproduction`

### 👀 Pull Request Review Process

1. A maintainer will review your PR, checking alignment with the linked Issue, code quality, and test coverage.
2. Address review comments with focused commits.
3. Re-run local validation after making changes.
4. Once approved, the maintainer will merge the PR into `main`.

### ✅ Definition of Done

An Issue or PR is considered **ready for review** when:

- [ ] The change is scoped to a single confirmed defect or approved feature.
- [ ] `ruff check .` and `pytest` pass locally.
- [ ] The `CHANGELOG.md` entry is drafted (for user-facing changes).
- [ ] Documentation is updated if behavior or flags changed.
- [ ] The PR description includes: linked Issue, summary, affected modules, and test evidence.
- [ ] No unrelated refactors or "while I'm here" changes are mixed in.

---

## 💻 Code & Documentation Standards

### 📐 Code Standards

- Use **Python 3.10+**.
- Keep modules focused: 1 file = 1 concern.
- Add **docstrings** to every new/changed function (PEP 257 style).
- Keep logging consistent: `[gh-finder]: message`. Use `logging.debug()` for verbose output.

### 📝 Comments and Docstrings

- **Docstrings are required** on every function that is not a trivial one-liner (PEP 257 style).
  A good docstring answers: *what does this function do, what does it return, and what exceptions can it raise?*
- **Inline comments explain *why*, not *what*.** If the code is self-explanatory, do not comment it.
  Use comments to record non-obvious decisions, workarounds, or constraints (e.g., `# GitHub resets quota at the top of the hour`).
- **Language:** American English, professional and direct. No emojis in code comments.
- **Tone:** Objective. Avoid humor, filler, or first-person narration inside code.
- **No commented-out code.** If code is no longer needed, delete it. Git preserves history.

### 🎯 Minimal Technical Footprint (Zero Over-Engineering)

- Solve the actual problem, not hypothetical future scenarios.
- Prefer surgical fixes over architectural rewrites.
- Avoid speculative abstractions without evidence.
- Reject premature optimization. Measure before abstracting.

### 🩹 Bugfix Scope Discipline

- Bugfix work must stay focused on the confirmed defect.
- Do not broaden the fix into unrelated refactors or feature work.
- Do not alter query assembly, export formats, or cache behavior as side effects.

### 🤖 AI-Assisted Contributions

AI tools may assist in code generation, documentation, or formatting, but all contributions remain subject to manual review.

- **Developer responsibilities:** Validate AI-generated code against project standards, test locally, and **clearly disclose AI assistance** in the PR description.

#### 📝 Example: AI Disclosure in PR Description

    This PR includes code generated with the assistance of GitHub Copilot for:
    - The `_handle_403()` function in `gh_finder/github_client.py`
    - Docstrings in `gh_finder/exporter.py`

    The code was reviewed, validated against project standards, and tested locally
    on Windows 11 (Python 3.12) by the author.

### 📚 Documentation Standards

- All project documentation should use a project-name-first visible title.
- First line of regular Markdown docs: `# 🕶️ gh-finder – <Document Title>`
- Write in professional American English.
- Use emojis sparingly (allowed in titles/headers, avoid in technical explanations).
- Quote relevant parts using blockquotes (`>`) when replying.

### 📏 Markdown Formatting Rules (CRITICAL)

All contributions to the repository (issues, comments, PRs, docs) must be written in Markdown. To ensure proper rendering across GitHub's interface:

- **Always close code blocks:** Every opening code block tag (e.g., ` ```bash `, ` ```json `, ` ```text `) **must be properly closed** with its corresponding closing triple backticks (` ``` `).

> ⚠️ Failing to close these tags *will break the Markdown layout for the entire post or issue*.

### 📜 License Header

gh-finder is licensed under the Mozilla Public License 2.0. Every source code file (`.py`) must include the following header at the top:

    # This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
    # If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/
    #
    # Original Author: Sergio Palma Hidalgo
    # Project URL: https://github.com/del-Pacifico/gh-finder
    # Copyright (c) 2025 Sergio Palma Hidalgo
    # All rights reserved.
    # [filename] - gh-finder

---

### 🚫 Common Mistakes to Avoid

Based on past reviews, these are the most frequent issues that delay PR merges:

1. **Mixing fixes with refactors.** A bugfix PR must not include "while I'm here" cleanups.
2. **Skipping local validation.** PRs that fail `ruff check .` or `pytest` are returned without review.
3. **Vague PR descriptions.** "Fixed the bug" is not enough. Link the Issue, describe scope, attach logs.
4. **Touching unrelated files.** If your PR touches `cli.py` but the Issue is about `exporter.py`, explain why.
5. **Forgetting the CHANGELOG.** User-facing changes without a CHANGELOG entry are not considered shipped.
6. **Opening Issues for questions.** Use GitHub Discussions first. Issues are for actionable work.

---

## ✅ Validation & Support

### 🧪 Local Validation

Run these checks before opening a pull request:

    ruff check .
    pytest

- `ruff check .` validates code style and catches common errors.
- `pytest` runs the test suite.

*Test results must be included as a comment in the associated Issue or PR.*

### 💬 Need Help?

- **For usage questions:** [GitHub Discussions](https://github.com/del-Pacifico/gh-finder/discussions)
- **For bug reports:** Use the `[Bug]` issue template.
- **For contribution help:** Comment on the issue, tag `@sergiopalmah` or `@AgentSmid`.

Contributions of all kinds are welcome — from typo fixes to major features. Let's build something great and useful together! 🚀
