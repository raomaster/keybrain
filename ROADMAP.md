# KeyBrain Roadmap

This roadmap tracks planned work for making KeyBrain reliable across coding agents while keeping the vault local-first and agent-agnostic.

## Near Term

### Universal KeyBrain skill

Goal: expose KeyBrain as one portable `keybrain` skill across coding agents, so users can ask naturally to search or save to their KB.

Status:

- Universal skill added at `setup/skills/keybrain/SKILL.md`.
- Installer attempts `npx skills@latest` for Claude Code, Codex, OpenCode, Copilot, Cursor, Gemini CLI, and Antigravity.
- Manual fallback copies the skill to known global skill paths, including Antigravity 2.0 and Antigravity CLI.
- Hermes and OpenClaw keep dedicated install paths because their skills/instructions are agent-specific.

Acceptance criteria:

- Claude Code can load `keybrain` from a standard skill directory and search KeyBrain when granted vault access.
- Codex can load `keybrain` from `~/.agents/skills` or `~/.codex/skills` and save/search when launched with vault access.
- Antigravity 2.0 can load the global `keybrain` skill from `~/.gemini/antigravity/skills`.
- Existing Hermes, OpenClaw, Copilot, and JetBrains flows keep working.

### Safer inbox processing

Goal: avoid surprising commits, pushes, or hard-coded agent behavior during inbox processing.

Planned work:

- Remove automatic `git commit && git push` from the `kb-process` skill or make it opt-in.
- Split processor execution from sync/publish behavior.
- Introduce clear flags for `process-only`, `commit`, and `push`.
- Keep cron behavior explicit and documented.

## Mid Term

### Agent adapter layer

Goal: make processing work with multiple agents without duplicating shell scripts.

Planned work:

- Add an agent runner abstraction for Claude, Codex, and future providers.
- Allow selecting the processing agent via environment variable, for example `KB_AGENT=claude|codex`.
- Keep Claude as the default processor until Codex parity is proven.
- Add tests for runner command construction.

### Project-local skill installation

Goal: optionally install `keybrain` into a repository workspace for teams and Antigravity Projects.

Planned work:

- Add `--install-scope global|project|both`.
- For project scope, install into `.agents/skills/keybrain/`.
- Keep global as the default because KeyBrain is personal memory across projects.
- Document sandbox limitations around ChromaDB and vault writes.

## Later

### Multi-agent memory consistency

Goal: keep memory coherent when Claude, Codex, OpenClaw, Copilot, and other agents all write to the same vault.

Planned work:

- Add conflict checks for concurrent inbox processing.
- Add stronger health checks for duplicate decisions and broken backlinks.
- Add a lock file or queue protocol for processors.
- Improve memory consolidation from multiple agent session formats.

## Non-goals For Now

- Replace the existing Claude cron processor immediately.
- Require a hosted service or API key.
- Move the ChromaDB index out of the local vault.
- Make Codex the default processor before sandbox/write behavior is documented and tested.
