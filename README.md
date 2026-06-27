# skills

Personal source repository for user-created agent skills (Cursor and Claude Code).

## Layout

```text
AGENTS.md            Repository-level rules (CLAUDE.md is a symlink to this)
skills/              Installable skills (copied verbatim into projects on install)
  workflows/         Non-coding, general agent workflows
  coding/            Coding-related skills
registry/            Management metadata (never installed)
  projects.yaml      Hand-maintained: project paths to scan
  upstream/          Pristine upstream snapshots for forks
  third-party.md     Generated: human-readable third-party ledger
  inventory.json     Generated: machine-readable ledger
```

Skills come in three classes:

- **Original** — purely self-created, at `skills/<category>/<skill>/SKILL.md`.
- **Fork** — a modified third-party skill. Installable copy at `skills/<category>/<skill>/`; pristine upstream snapshot at `registry/upstream/<skill>/` (see `registry/upstream/README.md`).
- **Third-party** — installed unmodified via `npx skills`; tracked only in the registry.

The registry ledger is generated, not hand-written:

```bash
node skills/workflows/manage-skills/scripts/sync-registry.mjs
```

## Validation

```bash
npx skills add ~/Coder/skills --list
```
