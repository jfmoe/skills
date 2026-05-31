# AGENTS.md

This repository is the personal source repository for user-created agent skills.

## Structure

- Self-created skills live under `skills/<category>/<skill>/SKILL.md`.
- Categories are limited to `skills/workflows/` and `skills/coding/`. Do not add new categories.
- `registry/third-party.md` records third-party global skills that are currently in use.
- Keep skill content and registry structure limited to `skills/workflows/`, `skills/coding/`, and `registry/third-party.md`.

## Categories

- `skills/workflows/`: non-coding, general agent workflows.
- `skills/coding/`: coding-related skills (docs lookup, dependency management, testing, code review, framework guidance, writing shell/launchd/automation/CI code).

## Registry

- Third-party global skills are recorded in `registry/third-party.md`; self-created skills are never recorded there.
- Only record third-party skills currently in use. Fields are `Skill`, `Source`, and `Scope`.
- Automatically maintain only global third-party records. Do not record project-level usage unless the user explicitly asks for a specific project.
- Do not auto-populate the registry from currently installed skill directories unless the user asks for an audit or inventory.

## Working Rules

- When creating, modifying, installing, updating, or recording skills, prefer the `manage-skills` skill if it exists. If it does not exist yet, follow this file and keep changes minimal.
- Do not manually edit installed/runtime skill directories such as `~/.agents/skills`, `~/.claude/skills`, `~/.cursor/skills`, or project `.agents/skills`.
- Use `npx skills ...` for installation and synchronization. Source edits belong in `~/Coder/skills`.
- Do not automatically commit or push unless the user explicitly asks.
- Use English in `README.md`, `AGENTS.md`, and skill files.

## Validation

After creating or modifying a skill, the default read-only validation is:

```bash
npx skills add ~/Coder/skills --list
```
