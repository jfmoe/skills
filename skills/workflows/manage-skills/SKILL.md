---
name: manage-skills
description: Create, update, install, synchronize, and record personal agent skills in ~/Coder/skills. Use when the user asks to create, edit, install, update, sync, or list personal skills, or to record a third-party skill.
---

# Manage Skills

Personal skill source repository: `~/Coder/skills` (remote `https://github.com/jfmoe/skills`). All source edits happen here; never hand-edit runtime install directories.

## Repository Setup

Before working on skills, ensure the source repo is present and current:

1. If `~/Coder/skills` is missing, clone it:

```bash
git clone https://github.com/jfmoe/skills ~/Coder/skills
```

2. If it exists and is a clean git repo, update it:

```bash
git -C ~/Coder/skills pull --ff-only
```

3. If it has local changes, do NOT pull. Continue with local content and report the dirty state.
4. If the path exists but is not a git repo, do not overwrite it; stop and report.

## Repository Layout

```text
skills/
  workflows/        Non-coding, general agent workflows
  coding/           Coding-related skills
registry/
  third-party.md    Third-party global skills in use
```

- Self-created skills: `skills/<category>/<skill-name>/SKILL.md`.
- `<skill-name>` is lowercase kebab-case (e.g. `manage-skills`, `macos-maintenance`).
- Only categories are `workflows` and `coding`; do not add others.
- For ops skills: general macOS maintenance/troubleshooting goes to `workflows/`; writing shell/launchd/automation/CI code goes to `coding/`.

## Creating or Editing a Skill

Only edit `~/Coder/skills/skills/<category>/<skill>/SKILL.md` when the user is creating or modifying a skill.

Each SKILL.md needs valid YAML frontmatter:

```markdown
---
name: skill-name
description: <what it does and when to use it, third person>
---
```

Add extra directories (scripts, examples, templates) only when the skill actually needs them.

After creating or editing, run read-only validation:

```bash
npx skills add ~/Coder/skills --list
```

## Installing and Syncing

Cursor or Codex reads `~/.agents/skills`, so target only `claude-code` by default. Let the `skills` CLI manage symlinks; do not write a custom symlink script.

Global (self-created):

```bash
npx skills add ~/Coder/skills -g -a claude-code --skill '*' -y
```

Project-level (self-created):

```bash
npx skills add ~/Coder/skills -a claude-code --skill '*' -y
```

Run install/update commands automatically when the user asks to install or update skills. If scope is ambiguous, ask whether they mean global or project-level — unless context clearly indicates personal global setup.

For the full set of CLI commands and options (`add`, `list`, `remove`, `update`, `find`, `init`), see [skills-cli.md](skills-cli.md).

## Third-Party Registry

Maintain `registry/third-party.md` only for GLOBAL third-party skill installs/removals.

- Record only third-party skills currently in use. Fields: `Skill`, `Source`, `Scope`.
- `Scope` is `global`, or a project path only when the user explicitly asks to record project-level usage.
- Never record self-created skills here.
- Do not auto-populate from installed directories unless the user asks for an audit or inventory.

## Rules

- Do not manually edit runtime install directories: `~/.agents/skills`, `~/.claude/skills`, `~/.cursor/skills`, or project `.agents/skills`.
- Do not auto-commit or auto-push; commit and push only when the user asks.
- Always read the relevant skill's content before acting on a skill-specific workflow.
