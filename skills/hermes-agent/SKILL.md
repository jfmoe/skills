---
name: hermes-agent
description: "Hermes Agent (Nous Research) is deployed on this machine. Use when a task involves Hermes — using, configuring, updating, or troubleshooting it — or touches `~/.hermes/`."
---

# Hermes Agent

Hermes Agent is a git install on this machine. This skill gives its layout, where to look things up, and the local maintenance rules. Hermes changes fast: take commands, flags, config keys, and providers from the sources below, not from memory.

## Layout

- **Home:** `~/.hermes/` — `config.yaml` (settings), `.env` (secrets), `auth.json`, `state.db`, `logs/`, `skills/`, `SOUL.md`. When `$HERMES_HOME` is set, it replaces `~/.hermes`.
- **Source:** `~/.hermes/hermes-agent/`, a git checkout of `NousResearch/hermes-agent`.
- **Entry points:** the CLI `~/.local/bin/hermes` (a wrapper around the source venv), the desktop app `/Applications/Hermes.app`, and the messaging gateway under launchd (`ai.hermes.gateway`). All three share one home, so a config or credential change affects all of them.

## Where to look

1. **Bundled skill:** `~/.hermes/hermes-agent/skills/autonomous-ai-agents/hermes-agent/SKILL.md`. Upstream maintains it and `hermes update` refreshes it. Read it first; its routing table points to a reference file per topic.
2. **Local docs:** `~/.hermes/hermes-agent/website/docs/`, the full doc site. Grep it.
3. **Web index:** `https://hermes-agent.nousresearch.com/docs/llms.txt`, one line per documented feature. Use it when the local docs do not answer.
4. **CLI help:** `hermes --help` and `hermes <command> --help` give the commands and flags of the installed version. Check them before you run a command.

## Maintenance rules

- **Source tree is read-only.** Change Hermes through the CLI, `config.yaml`, `.env`, and `~/.hermes/skills/`. Update only with `hermes update`; preview with `hermes update --plan`.
- **Settings and secrets stay apart.** Set settings with `hermes config set KEY VAL`; add credentials with `hermes auth`. `.env` holds secrets only. Never print or commit secret values.
- **Back up first, with the built-in tools.** Each tool prunes its own old copies, so do not add dated `.bak` files.
  - `config.yaml`: Hermes keeps copies in `backups/config/` automatically.
  - `.env`, `auth.json`, cron, and other state: run `hermes backup --quick --label <reason>`. Restore in a session with `/snapshot restore <id>`.
  - `SOUL.md`, `memories/`: the quick snapshot skips them. Copy the file to `<file>.bak`, overwriting the previous copy.
  - Before an update or a broad change: run `hermes backup` (full zip). `hermes import <zip>` restores it.
- **Restart to apply.** Tool and skill changes apply in a new session (`/reset`). Config changes apply after `hermes gateway restart` for the gateway and a relaunch for the CLI and desktop app.
- **Verify after a change.** Run `hermes config check` and `hermes doctor`; `hermes status` shows what is live; `hermes logs` shows errors.
