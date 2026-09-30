---
name: hermes-local
description: "Hermes Agent (Nous Research) is deployed on this machine. Use when a task involves Hermes — using, configuring, updating, or troubleshooting it — or touches `~/.hermes/`."
---

# Hermes Agent

Hermes Agent is a git install on this machine. This skill gives its layout, where to look things up, and the local maintenance rules. Hermes changes fast: take commands, flags, config keys, and providers from the sources below, not from memory.

## Layout

- **Home:** `~/.hermes/` — `config.yaml` (settings), `.env` (secrets), `auth.json`, `state.db`, `logs/`, `skills/`, `SOUL.md`. When `$HERMES_HOME` is set, it replaces `~/.hermes`.
- **Local git:** `~/.hermes/` is a git repository with no remote. Its whitelist `.gitignore` tracks only `config.yaml`, `SOUL.md`, `TRACKING.md`, and `scripts/`.
- **Source:** `~/.hermes/hermes-agent/`, a git checkout of `NousResearch/hermes-agent`.
- **Entry points:** the CLI `~/.local/bin/hermes` (a launcher script into the source install), the desktop app built from source by `hermes desktop` (`~/.hermes/hermes-agent/apps/desktop/release/mac-arm64/Hermes.app`), and the messaging gateway under launchd (`ai.hermes.gateway`). All three share one home, so a config or credential change affects all of them.

## Where to look

1. **Bundled skill:** `~/.hermes/hermes-agent/skills/autonomous-ai-agents/hermes-agent/SKILL.md`. Upstream maintains it and `hermes update` refreshes it. Read it first; its routing table points to a reference file per topic.
2. **Local docs:** `~/.hermes/hermes-agent/website/docs/`, the full doc site. Grep it.
3. **Web index:** `https://hermes-agent.nousresearch.com/docs/llms.txt`, one line per documented feature. Use it when the local docs do not answer.
4. **CLI help:** `hermes --help` and `hermes <command> --help` give the commands and flags of the installed version. Check them before you run a command.

## Maintenance rules

- **Source tree is read-only.** Change Hermes through the CLI, `config.yaml`, `.env`, and `~/.hermes/skills/`. Install and update skills with `hermes skills`. Update Hermes only with `hermes update`.
- **Custom plugins live in `jfmoe/hermes-plugins`.** Edit a plugin in `~/Coder/hermes-plugins/plugins/<name>/` and follow that repository's `AGENTS.md`; never edit the installed copy in `~/.hermes/plugins/`. Install with `hermes plugins install jfmoe/hermes-plugins/plugins/<name> --enable`. After you push a change, run `hermes plugins update <name>`. Before and after `hermes update`, run `hermes plugins compat` and `hermes plugins doctor <name>` for each custom plugin.
- **Review before every update.** Find what changed: run `hermes update --check`, then read `git -C ~/.hermes/hermes-agent log --oneline HEAD..origin/main` and the release notes (`gh release list -R NousResearch/hermes-agent`). Check each change against the local customizations: `config.yaml`, `.env`, `~/.hermes/TRACKING.md`, `SOUL.md`, plugins (`hermes plugins compat`), skills, cron jobs, and the gateway. `hermes update --plan` shows which services restart. If a change can break a customization, write an update plan (affected item, fix, rollback) and get the user's approval before you run `hermes update`. After the update, tell the user the version change, the notable changes, the effect on each customization, and the verification result.
- **Settings and secrets stay apart.** Set settings with `hermes config set KEY VAL`; add credentials with `hermes auth`. `.env` holds secrets only. Never print or commit secret values.
- **Own logins only.** Keep `auth.adopt_external_logins: false`. Hermes uses only its own logins (`hermes auth add <provider>`), so it never refreshes the Claude Code or Codex CLI login.
- **Back up first, with git and the built-in tools.** Do not add dated `.bak` files.
  - Git-tracked files: commit before and after each change (`git -C ~/.hermes`). Restore a file from an earlier commit. Hermes also keeps automatic `config.yaml` copies in `backups/config/`.
  - `.env`, `auth.json`, cron, and other state: run `hermes backup --quick --label <reason>`. Restore in a session with `/snapshot restore <id>`.
  - `memories/`: the quick snapshot and git skip it. Copy the file to `<file>.bak`, overwriting the previous copy.
  - Before an update or a broad change: run `hermes backup` (full zip). `hermes import <zip>` restores it.
- **Restart to apply.** Tool and skill changes apply in a new session (`/reset`). Config changes apply after `hermes gateway restart` for the gateway and a relaunch for the CLI and desktop app.
- **Verify after a change.** Run `hermes config check` and `hermes doctor`; `hermes status` shows what is live; `hermes logs` shows errors.
- **Tracking notes.** Before you update or reinstall Hermes, or change its update, credential, or `.env` settings, read `~/.hermes/TRACKING.md`. When an upstream issue blocks a local choice, add an entry there.
