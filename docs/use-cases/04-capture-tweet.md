# Use Case 4: Capture a Tweet or Social Media Post

**Goal:** Save a tweet or social media post to your knowledge base.

## Steps

1. Copy the tweet URL
2. In your terminal:
   ```bash
   kb "https://x.com/karpathy/status/1234567890"
   ```
3. When processed, the agent:
   - Fetches the tweet content via WebFetch
   - Extracts the text, author, date, and any media descriptions
   - Classifies and saves to the appropriate folder
   - Tags it with relevant topics

## Example: Karpathy tweet about LLMs

```bash
kb "https://x.com/karpathy/status/1234567890"
```

After processing, you'll have a file like:
```
raw/articles/2026-04-14-karpathy-on-llm-scaling.md
```

With frontmatter:
```yaml
---
title: "Karpathy on LLM Scaling Laws"
date: 2026-04-14
source: "https://x.com/karpathy/status/1234567890"
tags: [article, llm, twitter, karpathy]
status: raw
summary: "Andrej Karpathy discusses the implications of scaling laws..."
---
```

## Tips
- Works with any public social media post
- The agent extracts the full text even if the preview is truncated
- Thread content may require multiple saves
