# AGENTS.md

This repository is the personal source repository for user-created agent skills.

## Structure

- Self-created skills live flat at `skills/<skill>/SKILL.md`.
- Repository-managed skills have two classes: **Original** (self-created) and **Fork** (modified third-party — installable copy in `skills/<skill>/`, pristine snapshot in `registry/upstream/<skill>/`). Unmodified third-party skills stay outside this repository.
- `registry/upstream/<skill>/` holds pristine fork snapshots and provenance metadata, never installable skills.

## Operations

Creating, editing, installing, syncing, and forking skills are the `manage-skills` skill's job — the canonical operational home (`skills/manage-skills/SKILL.md`; `skills-cli.md` for CLI detail, ADR-0006 for the fork procedure). Prefer it for any skill operation.

## Agent skills

### Issue tracker

Issues are tracked in this repo's GitHub Issues (via the `gh` CLI). External PRs are **not** a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles using their default label strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
