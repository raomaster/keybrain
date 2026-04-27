# KeyBrain Roadmap

This roadmap tracks planned work for making KeyBrain reliable across coding agents while keeping the vault local-first and agent-agnostic.

## Near Term

### Codex knowledge capture

Goal: make Codex able to store durable notes, decisions, and findings in KeyBrain without replacing the existing Claude-based inbox processor.

Planned work:

- Add Codex-specific setup instructions for `~/.codex/AGENTS.md`.
- Document that Codex should be started with `--add-dir $KB_VAULT` when it needs to search or write the vault.
- Add a Codex use case for saving decisions with `kb "Decision: ..."`.
- Add a lightweight install helper that detects `~/.codex/AGENTS.md` and appends KeyBrain instructions idempotently.
- Keep the existing Claude cron flow unchanged until a Codex processor is explicitly implemented and tested.

Acceptance criteria:

- Codex can save a note to `$KB_VAULT/inbox/` using `kb`.
- Codex can run `kb-search-semantic` when launched with vault access.
- The installer can configure Codex without duplicating instructions on repeated runs.
- Existing Claude, OpenClaw, Copilot, and JetBrains flows keep working.

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

### Codex skills package

Goal: expose KeyBrain workflows to Codex as first-class reusable skills where supported.

Planned work:

- Create Codex-compatible skills for search, add, process, health, compile, and dream.
- Reuse existing agentskills.io content where possible.
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
