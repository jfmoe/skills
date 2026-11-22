# AGENTS.md

This repository is the personal source repository for user-created agent skills.

## Structure

- Self-created skills live flat at `skills/<skill>/SKILL.md`.
- Repository-managed skills have two classes: **Original** (self-created) and **Fork** (modified third-party — installable copy in `skills/<skill>/`, pristine snapshot in `registry/upstream/<skill>/`). Unmodified third-party skills stay outside this repository.
- `registry/upstream/<skill>/` holds pristine fork snapshots and provenance metadata, never installable skills.
- `reviews/zh/<skill>/` holds Chinese review mirrors of English-authored skills, regenerated on each source edit (see `manage-skills`).
- `prompts/` holds hand-pasted prompts: `lab/` (experimental, flat) and `stable/<type>/` (one level of type directories).

## Operations

Creating, editing, installing, syncing, and forking skills are the `manage-skills` skill's job — the canonical operational home (`skills/manage-skills/SKILL.md`; `skills-cli.md` for CLI detail, ADR-0006 for the fork procedure). Prefer it for any skill operation.

Recording, editing, finding, and promoting prompts under `prompts/` are the `manage-prompts` skill's job (`skills/manage-prompts/SKILL.md`), the single home for the prompt rules.

## Development workflow

Before editing `herdr-architect`, `ub-mode`, `test-layers`, or `commit-message`, read `docs/workflow.md`: these skills share rules, and it says which file owns each one.

## Agent skills

### Issue tracker

Issues are tracked in this repo's GitHub Issues (via the `gh` CLI). External PRs are **not** a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles using their default label strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
