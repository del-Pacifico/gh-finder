# 🕶️ gh-finder – Pull Request

Thank you for contributing! Please fill this out so reviews stay fast and predictable.

---

## 📋 Summary

Provide a concise summary of the changes introduced in this PR.

---

## 🔧 Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Enhancement (non-breaking improvement)
- [ ] Code refactor (no behavior change)
- [ ] Documentation update
- [ ] Build/CI/Repo tooling
- [ ] Other (please describe):

---

## 🧪 Related Issues

Reference any issues this PR addresses (e.g., Closes #42).

---

## 🧭 Branch Flow & Labels

- **Target branch:** `main` (MVP phase) or `dev` (post-MVP)
- **Source branch type:** `feature/*`, `fix/*`, `chore/*`, `docs/*`, `refactor/*`
- **Required labels:** `type:*`, `scope:*`, and applicable `priority:*`, `status:*`, or `needs:*`

---

## 🎯 Scope & Impact

- **User-facing change?** (CLI behavior, output, flags, docs)
  - [ ] Yes
  - [ ] No
- **Affected modules:** (`models`, `client`, `exporter`, `cli`, `cache`)
- **Expected behavior change:** (brief)

---

## ⚠️ Risk Assessment

- **Risk level:**
  - [ ] Low
  - [ ] Medium
  - [ ] High
- **Potential blast radius:** What could break?
- **Rollback plan:** How do we revert if needed?

---

## ✅ Testing Performed

Check what you actually ran.

**Automated checks:**

- [ ] `ruff check .`
- [ ] `pytest`

**Manual verification:**

- [ ] Tested with `--query`
- [ ] Tested with guided flags
- [ ] Tested `--output` (`.md` and `.json`)
- [ ] Tested without `GITHUB_TOKEN`
- [ ] Tested `--dry-run` and `--verbose`

**Python version tested:** (e.g., 3.12.1)
**OS tested:** (e.g., Windows 11, Ubuntu 24.04)

**Steps verified (short list):**
1.
2.
3.

---

## 🧾 Documentation & Changelog

- [ ] Documentation updated (README / `docs/PROJECT_FRAMEWORK.md`) if behavior or flags changed
- [ ] `CHANGELOG.md` updated for user-facing changes
- [ ] No documentation/changelog needed (refactor/tooling only)

---

## ✅ Checklist

- [ ] This PR targets the correct branch (`main` for MVP, `dev` post-MVP)
- [ ] Required repository labels were assigned (`type:*`, `scope:*`, and applicable lifecycle labels)
- [ ] The code follows the project's style guide (`ruff` passes)
- [ ] Local validation passes (`ruff check .` and `pytest`)
- [ ] Changes are modular, focused, and testable
- [ ] Error handling and edge cases were considered
- [ ] Code comments, logs, and user-facing messages use professional American English
- [ ] No sensitive information is exposed in this PR
- [ ] AI assistance disclosed (if applicable)

---

> For architecture and detailed specifications, refer to `docs/PROJECT_FRAMEWORK.md`.
> For user-facing changes, `CHANGELOG.md` is the source of truth.