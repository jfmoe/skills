# AGENTS.md Templates

Use these templates when creating a missing AGENTS.md or substantially restructuring a weak file. Keep only sections that are relevant to the repository.

## General Project Template

````markdown
# AGENTS.md

This file gives agent instructions for this repository.

## Commands

- `command` - Purpose and when to run it.

## Structure

- `path/` - Purpose and ownership boundary.

## Working Rules

- Project-specific instruction an agent must follow.

## Validation

Run before finishing relevant changes:

```bash
command
```
````

## Coding Repository Template

````markdown
# AGENTS.md

This file gives agent instructions for this repository.

## Commands

- `install-command` - Install dependencies.
- `dev-command` - Start the local development server.
- `test-command` - Run tests.
- `lint-command` - Run lint checks.
- `build-command` - Build production artifacts.

## Architecture

- `src/` - Application or library source.
- `tests/` - Test suite and fixtures.
- `config-file` - Important configuration and why it matters.

## Code Conventions

- Repository-specific style or abstraction rule.
- Preferred helper, framework, or pattern for common work.

## Generated Files

- `path/` - How it is generated and whether agents may edit it directly.

## Testing

- Use `test-command` for normal validation.
- Add focused tests near changed behavior when practical.

## Gotchas

- Non-obvious constraint, environment quirk, or integration detail.
````

## Monorepo Root Template

````markdown
# AGENTS.md

This file gives root-level instructions for this monorepo.

## Commands

- `command` - Root-level command and scope.

## Workspace Layout

- `apps/name/` - Application purpose.
- `packages/name/` - Shared package purpose.
- `tools/name/` - Tooling or automation purpose.

## Scope Rules

- Check for nested AGENTS.md files before editing within a package or app.
- Keep package-specific rules in that package's AGENTS.md.

## Shared Conventions

- Cross-workspace convention.

## Validation

- `command --filter package` - Validate a focused workspace change.
- `command` - Validate broad changes.
````

## Nested Package Template

````markdown
# AGENTS.md

These instructions apply within this directory.

## Package Purpose

Briefly state what this package/app owns.

## Local Commands

- `command` - Package-local command and when to use it.

## Local Rules

- Directory-specific constraint or convention.

## Validation

Run from this directory unless noted:

```bash
command
```
````

## Session-Learning Addition Template

Use this for small updates after a work session:

```markdown
- `command-or-pattern` - Durable reason this helps future agents.
```

Examples:

```markdown
- `npx skills add ~/Coder/skills --list` - Read-only validation for local skill source edits.
- Do not edit `dist/` directly; regenerate it with `npm run build`.
- Check nested `AGENTS.md` files before changing files under `packages/`.
```

## Placement Guidance

- Put repository-wide rules in the root AGENTS.md.
- Put package-specific commands and quirks in nested AGENTS.md files.
- Put personal preferences in local or global files only when the user asks.
- Do not copy a full root template into every nested file.
