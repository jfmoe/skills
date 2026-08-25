# skills

Personal source repository for user-created agent skills (Cursor and Claude Code).

## Layout

```text
AGENTS.md            Repository-level rules (CLAUDE.md is a symlink to this)
skills/              Installable skills (copied verbatim into projects on install)
  <skill>/           One folder per skill — flat, no category directories
registry/
  upstream/          Pristine upstream snapshots and provenance for forks
```

Repository-managed skills come in two classes:

- **Original** — purely self-created, at `skills/<skill>/SKILL.md`.
- **Fork** — a modified third-party skill. Installable copy at `skills/<skill>/`; pristine upstream snapshot at `registry/upstream/<skill>/` (see `registry/upstream/README.md`).
Unmodified third-party skills are installed directly from their upstream source and stay outside this repository.

## Validation

```bash
npx skills add ~/Coder/skills --list
```
