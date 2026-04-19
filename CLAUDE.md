# KeyBrain — Agent Instructions

This file instructs AI agents (Claude, Copilot, Cursor, etc.) on how to maintain and organize the KeyBrain knowledge vault.

> **Vault path:** The default is `$HOME/Knowledge`. Set the `KB_VAULT` environment variable to customize.
> All paths below use `$VAULT` to refer to your vault root.

## Vault Structure

```
$VAULT/
├── inbox/           ← ENTRY ZONE (only you add files here)
├── raw/
│   ├── articles/    ← articles, posts, web clips
│   ├── courses/     ← course notes and tutorials
│   ├── research/    ← papers, repos, technical research
│   └── projects/    ← READMEs and docs for your own projects
├── wiki/            ← EVERYTHING written by the agent — never edit manually
│   ├── _index.md    ← auto-maintained index
│   ├── concepts/    ← concept articles (LLMs, RAG, etc.)
│   └── technologies/← technology articles (Python, React, etc.)
├── decisions/       ← ADRs (Architecture Decision Records)
├── conversations/   ← exports from Claude/ChatGPT
│   └── YYYY-MM/
├── output/          ← slides, reports, generated visualizations
└── templates/       ← templates for each note type
```

---

## Inbox Processing

When asked to process `inbox/`, follow these steps for EACH file:

### Step 1: Read the content
Read the file completely. Determine the content type.

### Step 2: Classify

| Content signals | Type | Destination |
|----------------|------|-------------|
| Article URL, blog post, social media post | Article | `raw/articles/` |
| Paper, preprint, academic publication | Research | `raw/research/` |
| Course notes, lesson, tutorial, module | Course | `raw/courses/` |
| "I decided...", "going to use...", trade-offs, option comparison | Decision | `decisions/` |
| README, docs for your own project | Project | `raw/projects/` |
| Conversation export (Claude, ChatGPT, JSON/MD) | Conversation | `conversations/YYYY-MM/` |
| Loose idea, reflection, thought | Article | `raw/articles/` (with tag: idea) |

### Step 3: Create destination file

**Naming convention:** `YYYY-MM-DD-short-slug.md`
- Slug in lowercase, no accents, words separated by hyphens
- Example: `2026-04-10-why-i-use-obsidian.md`

**Required frontmatter for articles:**
```yaml
---
title: "Full article title"
date: YYYY-MM-DD
source: "URL or original source"
tags: [article, technology, topic]
status: raw
summary: "2-3 sentence summary explaining what it is and why it matters."
---
```

**Required frontmatter for decisions:**
```yaml
---
title: "Decision: <short title>"
date: YYYY-MM-DD
status: decided
tags: [decision, area]
area: "software | tools | learning | personal"
---
```

**Required frontmatter for courses:**
```yaml
---
title: "Course Name — Lesson/Module"
date: YYYY-MM-DD
course: "Full course name"
platform: "Udemy / YouTube / book / etc"
tags: [course, topic]
progress: "lesson X of Y"
---
```

### Step 3b: Detect if content is a URL

If the inbox file contains only a URL (or a URL with brief text), it's not the content — it's a pointer. Go fetch the real content:

**News / web articles** (any URL that isn't YouTube):
- Use `WebFetch` to retrieve the URL content
- Extract: title, author, publication date, article body
- Classify as article (`raw/articles/`)

**YouTube videos** (URL contains `youtube.com` or `youtu.be`):
1. Use markitdown to extract metadata and transcript:
   ```bash
   python3 -c "
   from markitdown import MarkItDown
   md = MarkItDown()
   result = md.convert('URL')
   print(result.text_content)
   "
   ```
2. Markitdown returns: title, keywords, runtime, description, and full transcript
3. The file in inbox may already contain this content (if processed by kb-add). If so, skip this step.
4. Classify by topic — may be article, course, or research
5. Do NOT use WebFetch or Playwright for YouTube — markitdown handles it

### Step 4: File content

For **articles**: include the full original content (or maximum possible), preceded by a 3-5 paragraph summary you write highlighting the most important points.

For **decisions**: use the ADR template format. Extract context, options considered, and decision from the user's text. If information is missing, mark sections with `[pending]`.

For **courses**: organize notes into: Key Concepts, Detailed Notes, Questions/To Explore, Code/Examples.

For **research**: include abstract, methodology, main findings, and why it's relevant.

### Step 4b: Add Connections section

At the end of every file you create or modify, add a `## Connections` section with relevant `[[wikilinks]]`. See the "Wikilinks — Mandatory Rule" section below.

### Step 5: Remove from inbox

After processing each file successfully, delete it from `inbox/`. Do not delete `.gitkeep`.

### Step 6: Update wiki/_index.md

Add a line to the index in the corresponding section:
```
- [Title](../path/to/file.md) — one-line summary
```

### Step 7: Update wiki/ if applicable

If the content introduces a concept or technology that deserves its own wiki article:
1. Check if an article about that topic already exists in `wiki/concepts/` or `wiki/technologies/`
2. If it doesn't exist and the topic is substantial enough (3+ files mention the topic): create a new wiki article
3. If it exists: add the new content as a section or update existing information
4. Add backlinks between related articles

---

## Wiki Maintenance

The wiki in `wiki/` is a compiled knowledge base, not raw notes. The agent is the only one who writes here.

### Wiki Articles

A wiki article must:
- Explain the concept/technology clearly and concisely
- Include backlinks to related vault articles
- Have sections: Description, Why It Matters, Resources in Vault (links to raw/)
- Update when new content about the same topic arrives

### Index (_index.md)

`wiki/_index.md` is the table of contents for the entire knowledge base. It must always be up to date. Format:

```markdown
# Knowledge Base Index
_Last updated: YYYY-MM-DD — X articles, Y decisions, Z courses_

## Recent articles
- [Title](path) — one-line summary — YYYY-MM-DD

## Concepts
- [Name](wiki/concepts/name.md) — brief description

## Technologies
- [Name](wiki/technologies/name.md) — brief description

## Decisions
- [Title](decisions/date-title.md) — decision in one line — YYYY-MM-DD

## Active courses
- [Name](raw/courses/...) — platform — progress
```

---

## Vault Queries

When the user asks about their stored knowledge:

1. Read `wiki/_index.md` first for orientation
2. Search relevant files using Glob and Grep
3. Synthesize the answer based on vault content
4. If information is missing or contradictory, mention it

### Typical questions you can answer:
- "What did I decide about X?"
- "What do I know about technology Y?"
- "What courses am I taking?"
- "What articles did I read about Z this month?"
- "Show me a summary of what I learned about LLMs"

---

## Health Checks (Periodic Maintenance)

When asked to do a "health check" of the vault:

1. **Consistency**: find articles without complete frontmatter, broken links, unprocessed files in inbox/
2. **Connections**: suggest new wiki articles where 3+ articles about the same topic exist in raw/
3. **Duplicates**: identify repeated or very similar content
4. **Impute missing data**: if articles lack summaries, add them

---

## Wikilinks — Mandatory Rule (Obsidian Graph View)

**Every file you create or modify must end with a `## Connections` section** containing `[[wikilinks]]` to related wiki articles. This feeds Obsidian's visual graph.

### How to choose connections

1. Read `wiki/_index.md` to see all existing wiki articles
2. Identify which ones are relevant to the file's content
3. Add the section at the end:

```markdown
## Connections

- [[article-name-wiki]]
- [[another-article]]
```

### Wiki articles available

This vault's wikilink definitions are stored in `wiki/_wikilinks.md`.
Read that file to see which `[[wikilinks]]` are available and when to use them.
This keeps wikilinks private and vault-specific without being overwritten by `kb update`.

---

## General Rules

- **Language**: Use the same language as the content source. Summaries can be in any language the user prefers.
- **Don't invent**: if the content doesn't say something, don't add it. Mark what's missing as `[pending]`.
- **Wikilinks mandatory**: every file ends with `## Connections`. No exceptions.
- **Date consistency**: always use `YYYY-MM-DD` format.
- **No empty files**: don't create files with just frontmatter. If there's not enough content, don't create the file yet.
- **memory/ is not inbox**: never process `memory/` files with kb-process. They are episodic session logs, not classifiable content.
- **MEMORY.md is not wiki**: never edit MEMORY.md manually or include it in wiki compilation. It is rebuilt by kb-dream.
