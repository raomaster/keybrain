# Use Case 6: Record a Technical Decision

**Goal:** Save an Architecture Decision Record (ADR) to your vault.

## Steps

1. Tell your agent about the decision:
   ```
   kb "Decided to use PostgreSQL over MongoDB because our data is highly relational and we need ACID transactions for the payment system."
   ```
2. Or be more explicit in Claude Code:
   ```
   /kb-add "Decisión: Usar PostgreSQL en vez de MongoDB — Por qué: datos altamente relacionales, necesitamos transacciones ACID para pagos — Descartado: MongoDB (no soporta JOINs eficientes), SQLite (no soporta concurrencia)"
   ```
3. When processed, the agent:
   - Classifies it as a decision
   - Creates an ADR in `decisions/` with the standard format
   - Includes: Context, Options considered, Decision, Consequences

## ADR format

The agent creates files like `decisions/2026-04-14-postgresql-over-mongodb.md`:

```yaml
---
title: "Decision: PostgreSQL over MongoDB"
date: 2026-04-14
status: decided
tags: [decision, database]
area: "software"
---
```

With sections: Context, Options considered, Decision, Consequences.

## Tips
- Use natural language — the agent extracts the decision from your text
- The agent marks missing information as `[pending]`
- Decisions appear in the Obsidian graph connected to related concepts
