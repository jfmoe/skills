---
name: hermes-agent
description: "Configure, run, or troubleshoot an already-installed Hermes Agent (Nous Research's agent framework) — switch its model/provider, edit config, run it day-to-day (chat/TUI/sessions/cron/send), or repair it (updates, rollback, doctor, logs, backups). Triggers on 'Hermes is broken', 'change Hermes's model', or mentions of `~/.hermes/`, `~/.local/bin/hermes`, `/Applications/Hermes.app`. Not for first-time install, source contribution, or Windows-only issues."
---

# Hermes Agent — Operations

Hermes Agent (Nous Research) is already installed on this machine. This skill helps you **configure, run, and troubleshoot** it. It does not cover first-time install, source-code contribution, or Windows.

Hermes changes fast, so stale-prone lists (subcommands, providers, config sections, slash commands, symptoms) are **not** copied here — you discover those live at runtime. This skill keeps only the stable stuff: the two hard rules, machine facts, workflows, safety norms, and gotchas.

## Two hard rules (these outrank answering from memory)

**Rule 1 — When unsure or uncovered, consult the docs. Do not guess.**
This machine has the **complete doc set locally** (git install) — prefer it over the web; it's the same content, offline and greppable. The docs root is:

```
~/.hermes/hermes-agent/website/docs/        # 339 .md files, full Docusaurus site
```

Grep/glob there to find the relevant guide (e.g. `grep -ril <topic> ~/.hermes/hermes-agent/website/docs/`), then read the file. Key sections: `user-guide/`, `integrations/`, `reference/`, `developer-guide/`. If the local docs are absent (non-git install) or you still can't find it, fall back to the web index and route from it to the specific guide URL:

```
https://hermes-agent.nousresearch.com/docs/assets/files/llms-d4972c57170916efd83766ae50c3bb3d.txt
```

Never invent commands, flags, config keys, or provider names.

**Rule 2 — Verify exact command flags/arguments with `--help` before running.**
Hermes's subcommands and flags shift between versions. Before you run any specific command, check it live:

```bash
hermes <subcommand> --help        # e.g. hermes config --help, hermes auth --help
```

Do not reconstruct flags from memory. The `--help` output is the source of truth for what exists right now.

## Machine facts (stable structure — use for orientation)

- **Home:** `~/.hermes/` — config (`config.yaml`), secrets (`.env`), `auth.json`, `logs/`, `sessions/`, `state.db`, `skills/`, source at `~/.hermes/hermes-agent/`.
- **GUI and CLI share the same home.** `/Applications/Hermes.app` and the CLI `~/.local/bin/hermes` both run against `~/.hermes/`. The CLI is a thin bash wrapper that `exec`s `~/.hermes/hermes-agent/venv/bin/hermes`. **Any config/auth change affects both GUI and CLI.** There is no separate per-surface config.
- **Source install:** `.install_method=git` (the file `~/.hermes/.install_method`), source in `~/.hermes/hermes-agent/`. Official updates go through `hermes update`, which can take a pre-update backup (see `hermes update --help`; gated by `updates.pre_update_backup`, off by default here). Don't assume a fixed backup path — locate backups per `reference/troubleshooting.md`.
- **Full docs are local:** `~/.hermes/hermes-agent/website/docs/` holds the complete Docusaurus doc site (339 `.md` files). Prefer it over the web. `hermes update` replaces the source dir but keeps this relative path stable.
- A local copy of Hermes's own bundled ops skill lives at `~/.hermes/skills/autonomous-ai-agents/hermes-agent/SKILL.md` — useful as a fuller (but list-heavy, faster-staling) reference. Its lists are exactly what this skill routes around; treat its **stable** guidance (safety, gotchas) as aligned with the rules below.

## Routing — intent → reference file + discovery command

| You want to… | Read | Discover current truth with |
|---|---|---|
| Configure / switch provider or model, edit any config | `reference/config-editing.md` | `~/.hermes/config.yaml` or `hermes config show`; `hermes model`; `hermes config --help`, `hermes auth --help` |
| Run / use it day-to-day (chat, TUI, sessions, cron, send) | `reference/operations.md` | `hermes --help`; `hermes <cmd> --help`; `/help` in-session |
| Diagnose / maintain / update / roll back | `reference/troubleshooting.md` | `hermes doctor`, `hermes status`, `hermes logs` |

**Discovery commands (what exists right now, never copied into this skill):**

- Subcommands: `hermes --help`, then `hermes <cmd> --help` for flags.
- Config: read `~/.hermes/config.yaml` directly, or `hermes config show`; paths via `hermes config path` / `hermes config env-path`.
- Tools: `hermes tools list`. Skills: `hermes skills list`. Providers/models: `hermes model`.
- In-session slash commands: `/help`.
- Anything deeper or uncovered: **Rule 1** — grep the local docs at `~/.hermes/hermes-agent/website/docs/` (full offline doc set), web index only as fallback.

## Safety norms (aligned with Hermes's bundled autonomous-ai-agents skill)

These are adopted directly from Hermes's own ops skill — don't invent a parallel set. The full editing norms (dedicated `config`/`auth` commands, config-vs-`.env` split, validation) live in `reference/config-editing.md`; the front-door essentials:

- **Secrets:** API keys go through `hermes auth`, not hand-edited `.env`. Never print secrets in plaintext or commit them to any repo.
- **`security.redact_secrets` is on by default** and snapshotted at process startup — toggling it mid-session does NOT take effect (needs a restart). Deliberate, so an LLM can't disable redaction on itself mid-task.
- **Command approval (`approvals.mode`):** `manual` (default — prompts before destructive commands) / `smart` / `off` (equivalent to `--yolo`). YOLO / `off` does NOT disable secret redaction; they're independent. Confirm before destructive actions in `manual` environments.
- **Changes need a restart to apply** — full mapping (tool/skill → `/reset`, config → `/restart` or relaunch) in `reference/troubleshooting.md`.
