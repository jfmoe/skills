# AGENTS.md

This repository is the personal source repository for user-created agent skills.

## Structure

- Self-created skills live flat at `skills/<skill>/SKILL.md` — no category directories (ADR-0004).
- Three classes: **Original** (self-created), **Fork** (modified third-party — installable copy in `skills/<skill>/`, pristine snapshot in `registry/upstream/<skill>/`), **Third-party** (installed unmodified; only tracked in the registry).
- `registry/` holds management metadata, never installable skills: `projects.yaml` (the only hand-maintained input), `upstream/<skill>/` (fork snapshots), `ledger.yaml` (generated).

## Invariants

- Never hand-edit runtime install dirs (`~/.agents/skills`, `~/.claude/skills`, `~/.cursor/skills`, project `.agents/skills`) — let `npx skills` manage them. Source edits belong in `~/Coder/skills`.
- Never hand-edit the generated `registry/ledger.yaml`; regenerate it instead.
- Keep skill folders clean: everything under `skills/<skill>/` is copied verbatim into projects on install, so never put management metadata (tests, snapshots) there.
- A fork keeps two copies; the snapshot's `SKILL.md` is renamed to `SKILL.md.orig`, else `npx skills` registers it as installable (ADR-0001).

## Operations

Creating, editing, installing, syncing, forking, and regenerating the ledger are the `manage-skills` skill's job — the canonical operational home (`skills/manage-skills/SKILL.md`; `skills-cli.md` for CLI detail, ADR-0006 for the fork procedure). Prefer it for any skill operation.

## Agent skills

### Issue tracker

Issues are tracked in this repo's GitHub Issues (via the `gh` CLI). External PRs are **not** a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles using their default label strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
