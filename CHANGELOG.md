# Changelog

All notable changes to KeyBrain will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Fixed
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
