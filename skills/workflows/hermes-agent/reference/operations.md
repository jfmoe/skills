# Day-to-Day Operations

Stable run **patterns**. Exact flags and the full subcommand list go stale — confirm with `hermes <cmd> --help` before running (SKILL.md Rule 2), and discover what exists with `hermes --help`. For anything uncovered, fetch the docs index (Rule 1).

## Running it

- **Interactive (default):** `hermes` drops straight into chat. Force a surface with `hermes chat --tui` or `hermes chat --cli`.
- **One-shot / scriptable:** `hermes chat -q "…"` runs a single query non-interactively. The top-level `hermes -z "…"` (`--oneshot`) prints only the final response text (no banner/spinner/tools preview) — intended for pipes and scripts; approvals are auto-bypassed in this mode, so treat it accordingly.
- **Continue a conversation:** `--continue` (most recent, or by name) / `--resume <session-id>`. These are flags, not subcommands — `hermes chat --help` for the exact forms.
- **GUI / desktop app:** `hermes desktop` (alias `hermes gui`) builds and launches the Electron app. It shares the same `~/.hermes/` home as the CLI.

## Sessions

`hermes sessions` manages the session store (list, browse, rename, export, prune, delete, stats). Subcommands and their flags shift — run `hermes sessions --help`. In-session, `/resume`, `/branch`, and history commands are available via `/help`.

## Automation

- **Scheduled jobs:** `hermes cron` (create/list/edit/pause/resume/run/remove). Schedules accept durations (`30m`), "every" phrases, 5-field cron, or ISO timestamps. `hermes cron --help`, then the specific subcommand's `--help`. Prefer cron over spawning processes for recurring work — it handles delivery and retry.
- **Send a message to a configured platform** (from scripts/cron/CI, no agent loop): `hermes send` — reuses the gateway's platform credentials. `hermes send --list` shows available targets; `hermes send --help` for target syntax (`platform`, `platform:chat_id`, `platform:#channel`).

## In-session slash commands

Type `/help` inside a chat session for the current, authoritative list — it is not copied here because new commands land often. (A handful recur in this skill's workflows: `/reset` for a new session, `/restart` for the gateway.)

## Deeper areas (one-line pointers — not expanded here)

These exist and are powerful, but are out of this skill's day-to-day scope. When you actually need one, fetch its guide from the docs index (Rule 1):

- **Multi-instance / tmux orchestration** and **`delegate_task`** for parallel or long-running agents.
- **delegation**, **curator** (background skill maintenance), and **kanban** (multi-agent work queue) subsystems.
- **MCP servers**, **plugins**, **profiles**, **webhooks**, and **gateway** platform setup.

The local bundled skill at `~/.hermes/skills/autonomous-ai-agents/hermes-agent/SKILL.md` has worked examples for spawning and tmux orchestration if you need a starting point.
