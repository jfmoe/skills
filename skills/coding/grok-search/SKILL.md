---
name: grok-search
description: Use when the user asks for fresh Web search, X/Twitter search, recent posts, current events.
---

# Grok Search

Use a configured grok2api endpoint to ask Grok multi-agent console models for fresh Web or X evidence.

## Steps

1. Choose the effort.
   Use `medium` by default. Use `low` for simple probes, `high` for harder synthesis, and `xhigh` only when the task justifies the slowest run.

   Completion criterion: exactly one effort is chosen.

2. Run the CLI immediately.
   From this skill directory:

   ```bash
   node scripts/grok-search.mjs --query "latest context to verify" --effort medium
   ```

   Options: `--effort low|medium|high|xhigh`, `--effort-model reasoning|alias`, `--format text|json`, `--base-url`, `--api-key`, `--model`, `--timeout-ms`. `GROK_SEARCH_MODEL` defaults to `grok-4.20-multi-agent-console`; `GROK_SEARCH_EFFORT` defaults to `medium`. Use `node scripts/grok-search.mjs --help` as the CLI source of truth.

   Completion criterion: the script returns an answer, or a specific configuration, HTTP, JSON, or timeout error.

3. Handle missing configuration only after failure.
   If the CLI reports `Missing base URL` or `Missing API key`, tell the user to set `GROK_SEARCH_BASE_URL` and `GROK_SEARCH_API_KEY`, or pass `--base-url` and `--api-key`.

   Completion criterion: the user knows exactly which missing setting blocked the search.

4. Report evidence.
   State that the answer came from Grok Web/X search through grok2api. Preserve source names, URLs, citations, and quoted snippets only when the model returned them. Do not invent `search_sources` or citations.

   Completion criterion: the user can distinguish searched evidence from your own inference.
