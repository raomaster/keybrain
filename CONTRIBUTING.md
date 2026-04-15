# Contributing to KeyBrain

Thank you for your interest in contributing! KeyBrain is an open-source framework for AI-powered personal knowledge management.

## How to report bugs

Open an issue with:
- **OS and version** (macOS 15, Ubuntu 24.04, Windows 11, etc.)
- **KeyBrain version** (from `cat $KB_VAULT/VERSION`)
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Relevant logs** (from `$KB_VAULT/logs/`)

## How to propose features

Open an issue with:
- **Problem:** What problem does this solve?
- **Proposed solution:** How should it work?
- **Alternatives considered:** What else did you evaluate?

## How to contribute skills

KeyBrain skills live in `setup/skills/`. Each skill is a directory with a `skill.md` file.

Requirements for `skill.md`:
- Must have a YAML frontmatter with `description` field
- If the description contains `: `, wrap it in double quotes
- Must include a test section with manual verification steps
- Must be in English (translations welcome as separate PRs)

## Pull requests

1. Fork the repo and create a feature branch
2. Write tests for new functionality
3. Ensure all tests pass: `python3 -m pytest tests/ -v`
4. Ensure smoke tests pass: `bash setup/test-install.sh`
5. Add a CHANGELOG entry under `[Unreleased]`
6. Submit PR with clear description of changes

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Please read it before participating.
