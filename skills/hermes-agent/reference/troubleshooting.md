# Troubleshooting & Recovery

Stable diagnostic and rollback **processes**. Symptom lists go stale and are not copied here — when a symptom isn't covered, fetch the docs index (SKILL.md Rule 1). Confirm flags with `hermes <cmd> --help` before running (Rule 2).

## Diagnostic triad (start here, in order)

1. `hermes doctor` — checks config and dependencies. `hermes doctor --fix` attempts automatic fixes. It also surfaces security advisories (ack with `hermes doctor --ack <id>`).
2. `hermes status` — component status; `hermes status --all` for a redacted full view, `--deep` for slower thorough checks.
3. Logs — `hermes logs` (defaults to `agent.log`, last 50 lines). Useful flags: `-f` (follow), `--level ERROR`, `--component gateway|agent|cron`, `--since 1h`, `hermes logs list` to see available files. Files live under `~/.hermes/logs/`.

## Common failure shapes (process, not symptom catalog)

- **Model / provider not working:** `hermes doctor` first → re-authenticate the provider with `hermes auth` (or `hermes auth add <provider>`) → confirm the key/credential exists. See `reference/config-editing.md` for the full provider workflow.
- **A change didn't take effect:** this is almost always a restart issue, not a broken edit.
  - Tool / skill changes → `/reset` (new session); they don't apply mid-conversation.
  - Config changes → `/restart` the gateway, or exit and relaunch the CLI.
  - Source-code changes → restart the process entirely.
- **Update broke the install / rollback:** restore a backup zip with `hermes import <zipfile>` (`--force` to overwrite). Backups are zip files, not a fixed directory — `hermes backup` writes one (default `~/hermes-backup-<timestamp>.zip`; `--quick` for just critical state), and `hermes update` can take a pre-update one. Locate candidates with `ls ~/hermes-backup-*.zip` and confirm paths via `hermes backup --help` / `hermes update --help`. A `~/.hermes/hermes-agent.broken-<timestamp>` directory is the old source set aside by a failed/risky `hermes update` — a leftover, not active. Filesystem checkpoints (the `/rollback` history) are managed via `hermes checkpoints` (`status` / `prune` / `clear`).
- **Retired / deprecated model or settings after an update:** `hermes config migrate` for general config; `hermes migrate` for specific retired models (`hermes migrate --help`).
- **Anything else / deeper:** consult the local docs (Rule 1) — start with `~/.hermes/hermes-agent/website/docs/reference/faq.md`, or `grep -ril <symptom> ~/.hermes/hermes-agent/website/docs/`. The local bundled skill at `~/.hermes/skills/autonomous-ai-agents/hermes-agent/SKILL.md` has a longer (faster-staling) troubleshooting section worth skimming for gateway/platform-specific cases.

## Recovery sequencing (when an update or edit left it broken)

1. **Diagnose before changing anything** — `hermes doctor` and `hermes status` to see what's actually wrong; check `hermes logs --level ERROR`.
2. **Snapshot current state** — `hermes backup --quick` before you start undoing things, so a bad recovery is itself reversible.
3. **Restore the most recent good backup** — `hermes import <zipfile>` (locate the zip per the rollback note above).
4. **Re-validate** — `hermes config check`, then `hermes doctor` again; relaunch and confirm with `hermes status`.
