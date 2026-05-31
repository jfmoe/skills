# skills

Personal source repository for user-created agent skills (Cursor and Claude Code).

## Layout

```text
AGENTS.md            Repository-level rules (CLAUDE.md is a symlink to this)
skills/
  workflows/         Non-coding, general agent workflows
  coding/            Coding-related skills
registry/
  third-party.md     Third-party global skills currently in use
```

Self-created skills live at `skills/<category>/<skill>/SKILL.md`.

## Validation

```bash
npx skills add ~/Coder/skills --list
```
