# Changelog

All notable changes to KeyBrain will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] - 2026-04-27
### Added
- `KB_PROCESS_AGENT` to select the inbox processing backend (`opencode` by default, `claude` optional).
- Installer detection and prompt for OpenCode vs Claude Code during setup.
- `KB_VENV` and `KB_CHROMADB` support to keep runtime artifacts outside synced vaults.

### Changed
- `process-inbox.sh` now uses OpenCode by default for corporate environments where Claude Code is not approved.
- Python wrappers now respect `KB_VENV` and support both Unix `bin/python3` and Windows `Scripts/python.exe` virtual environments.

### Fixed
- `kb process` no longer requires Claude login when OpenCode is configured.
- `process-inbox.sh` re-indexing works when the Python runtime lives outside `$KB_VAULT`.

## [0.3.0] - 2026-04-27
### Added
- `ROADMAP.md` with the planned path for Codex knowledge capture, safer inbox processing, and future multi-agent adapter support.
- Codex support: `configure_codex_agents_md` installs `~/.codex/AGENTS.md` idempotently with KeyBrain instructions, including `--add-dir $KB_VAULT` note for vault search access.
- `KB_AUTO_COMMIT` and `KB_AUTO_PUSH` env vars for `process-inbox.sh`: git operations are fully opt-in — the vault may live in Google Drive, OneDrive, or any backup system that doesn't use git.

### Changed
- Repositioning: KeyBrain framed as persistent memory and research base for AI coding agents (Claude Code, Copilot, Cursor) instead of generic personal knowledge base
- README rewrite: new tagline, new "What is KeyBrain?" section, new "Why KeyBrain?" section with Karpathy reference, install prompt aligned to agent-memory framing
- Repo URL placeholder replaced with actual `raomaster/keybrain`

### Fixed
- `kb-process` skill: removed automatic `git commit && git push` step — vault may live in Google Drive, OneDrive, or any non-git backup system.
- `process-inbox.sh`: removed automatic git commit and push — both are now opt-in via `KB_AUTO_COMMIT=true` and `KB_AUTO_PUSH=true` env vars.
- YouTube URLs in `kb-add` now use markitdown to extract title, description, and transcript directly
- `process-inbox` uses markitdown for YouTube instead of WebFetch/Playwright
- `kb-update` version comparison (strip `v` prefix from git tags)

## [0.1.0] - 2026-04-14
### Added
- Vault structure (inbox, raw, wiki, decisions, conversations)
- `kb` CLI with `KB_VAULT` env var for configurable paths
- install.sh (macOS, Linux, WSL2) + install.ps1 (Windows)
- Platform detection and interactive path selection
- markitdown for multi-format inbox (PDF, Word, Excel, PPT, YouTube)
- ChromaDB for local semantic search
- Multi-agent skills via agentskills.io (7 skills: add, capture, compile, health, permissions, process, search)
- `kb update` with agent notification
- Self-documenting initial content (articles, ADR, wiki index)
- Step-by-step use cases (7 scenarios)
- CI with GitHub Actions (macOS + Ubuntu 24.04)
- CONTRIBUTING.md + CODE_OF_CONDUCT.md
- ChatGPT import tool (`kb-import-chatgpt`)
- Post-commit git hook for automatic commit capture
- Unit tests for CLI, inbox processing, and indexing
