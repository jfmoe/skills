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
skills/                 Installable skills (copied verbatim into projects)
  <skill>/              One folder per skill — flat, no category directories
registry/               Management metadata (never installed)
  projects.yaml         Hand-maintained: project paths to scan
  upstream/<skill>/     Pristine upstream snapshots for forks
  ledger.yaml           Generated: cross-project third-party + fork ledger
```

- `<skill-name>` is lowercase kebab-case (e.g. `manage-skills`, `macos-maintenance`); flat, no category directories (ADR-0004).
- Three classes: **original** (self-created), **fork** (modified third-party — see Forking), **third-party** (installed unmodified, tracked only in the registry).
- Never put management metadata inside `skills/<skill>/`; everything there is copied into projects on install.

## Creating or Editing a Skill

Only edit `~/Coder/skills/skills/<skill>/SKILL.md` when the user is creating or modifying a skill.

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

Default target is `-a codex claude-code`: `codex` writes `.agents/skills` (read by Cursor and Codex), `claude-code` writes `.claude/skills`. Let the `skills` CLI manage symlinks; do not write a custom symlink script. See [skills-cli.md](skills-cli.md) for how the target choice affects copy vs symlink mode.

Global (self-created):

```bash
npx skills add ~/Coder/skills -g -a codex claude-code --skill '*' -y
```

Project-level (self-created):

```bash
npx skills add ~/Coder/skills -a codex claude-code --skill '*' -y
```

Run install/update commands automatically when the user asks to install or update skills. If scope is ambiguous, ask whether they mean global or project-level — unless context clearly indicates personal global setup.

For the full set of CLI commands and options (`add`, `list`, `remove`, `update`, `find`, `init`), see [skills-cli.md](skills-cli.md).

## Forking a Third-Party Skill

A fork is a third-party skill you modified. Keep two copies — a clean installable one and a pristine snapshot for diffing.

To create a fork:

1. Fetch the upstream skill into a temp dir, noting its `ref` and `commit`.
2. Save the pristine files to `registry/upstream/<skill>/`. **Rename every `SKILL.md` to `SKILL.md.orig`** — `npx skills` registers any literal `SKILL.md` in the repo as installable (verified; there is no ignore option). Keep other files as-is.
3. Write `registry/upstream/<skill>/meta.yaml`. This is the canonical `meta.yaml` schema:

```yaml
source: owner/repo                 # upstream github source (or URL)
ref: main                          # branch or tag fetched
commit: <sha>                      # exact commit fetched
upstream_path: path/in/source      # skill subpath inside the source repo
local_path: skills/<skill>         # the modified copy in this repo
fetched_at: YYYY-MM-DD             # fetch date
notes: |                           # human provenance: what changed and why
  - what changed
```

   `notes` is human provenance, not inventory data — it is intentionally absent from the generated ledger. Do not "fix" that.

4. Copy the upstream into `skills/<skill>/SKILL.md` as the starting point and apply your changes.
5. Validate: `npx skills add ~/Coder/skills --list` must show the fork as ONE skill (the snapshot must not appear).
6. Regenerate the ledger (below).

To update a fork from upstream — three-way compare:

- A = freshly fetched upstream (temp)
- B = `registry/upstream/<skill>/` (old pristine)
- C = `skills/<skill>/SKILL.md` (your modified copy)

Diff A↔B for the upstream delta, port the wanted parts into C, then overwrite B with A and bump `commit` / `fetched_at` / `notes` in `meta.yaml`. Regenerate the ledger.

## Registry (generated)

`registry/ledger.yaml` is GENERATED — never hand-edit it.

- The only hand-maintained input is `registry/projects.yaml` (project paths to scan). Add/remove paths there as the user installs third-party skills into projects.
- Regenerate after any third-party install/remove/fork or after editing `projects.yaml`:

```bash
node skills/manage-skills/scripts/sync-registry.mjs
```

- Data sources: global lock `~/.agents/.skill-lock.json`, each project's `skills-lock.json`, and fork `meta.yaml` files. Self-created skills (`jfmoe/skills` / local to this repo) are excluded.
- Per-project reproducibility belongs to each project's `skills-lock.json` (`npx skills experimental_install` restores from it); the ledger is only a cross-project overview.
- Review the git diff after regenerating; output is deterministic, so a clean run yields no spurious changes.

## Rules

- Do not manually edit runtime install directories: `~/.agents/skills`, `~/.claude/skills`, `~/.cursor/skills`, or project `.agents/skills`.
- Always read the relevant skill's content before acting on a skill-specific workflow.
