# skills

Personal source repository for user-created agent skills (Cursor and Claude Code).

## Layout

```text
AGENTS.md            Repository-level agent rules
skills/              Installable skills (copied verbatim into projects on install)
  <skill>/           One folder per skill — flat, no category directories
registry/
  upstream/          Pristine upstream snapshots and provenance for forks
prompts/             Hand-pasted prompts: lab/ (experimental) and stable/<type>/
```

Repository-managed skills come in two classes:

- **Original** — purely self-created, at `skills/<skill>/SKILL.md`.
- **Fork** — a modified third-party skill. Installable copy at `skills/<skill>/`; pristine upstream snapshot at `registry/upstream/<skill>/` (see `registry/upstream/README.md`).
Unmodified third-party skills are installed directly from their upstream source and stay outside this repository.

## Development workflow

`docs/workflow.md` explains how `herdr-architect`, `ub-mode`, `test-layers`, and `commit-message` combine with the third-party engineering skills into one spec-to-merge workflow: principles, roles, installation, and maintenance.

## Validation

```bash
npx skills add ~/Coder/skills --list
```
