---
name: manage-skills
description: Use when the user asks to create, edit, install, update, sync, list, or fork personal skills.
---

# Manage Skills

Personal skill source repository: `~/Coder/skills` (remote `https://github.com/jfmoe/skills`). All source edits happen here; never hand-edit runtime install directories.

## Repository Setup

Before working on skills, ensure the source repo is present and current:

1. If `~/Coder/skills` is missing, clone it:

```bash
git clone https://github.com/jfmoe/skills ~/Coder/skills
```

2. If it has local changes, do NOT pull. Continue with local content and report the dirty state.
3. If the path exists but is not a git repo, do not overwrite it; stop and report.

## Repository Layout

```text
skills/                 Installable skills (copied verbatim into projects)
  <skill>/              One folder per skill — flat, no category directories
registry/
  upstream/<skill>/     Pristine upstream snapshot and provenance for a fork
```

- Repository-managed skills have two classes: **original** (self-created) and **fork** (modified third-party — see Forking). Unmodified third-party skills stay outside this repository.

## Creating or Editing a Skill

Only edit `~/Coder/skills/skills/<skill>/SKILL.md` when the user is creating or modifying a skill.

After creating or editing, run read-only validation:

```bash
npx skills add ~/Coder/skills --list
```

## Chinese Review Mirrors

An English-authored skill gets a Chinese review mirror under `reviews/zh/<skill>/`, mirroring the source layout: `SKILL.md` becomes `SKILL.zh.md` (any literal `SKILL.md` in the repo registers as installable); other files keep their names. Chinese-authored skills have no mirror.

- Mirrors are plain translations — no annotations or provenance headers. Regenerate them from source; never hand-edit.
- After creating or editing an English skill's `.md` files, regenerate its mirror files in the same commit. The post-edit `--list` validation must show an unchanged skill set.
- Review feedback given in Chinese is applied to the English source; the source stays canonical.

## Installing and Syncing

An explicitly named single agent is a private target: verify its native skill directory and install only there. Never fall back to project or global `.agents/skills`; use those only for shared multi-agent installs or explicit requests. If the native target is unknown, stop and report.

When the user does not name an agent, default targets are `-a codex claude-code`. Project scope is the CLI default; `-g` selects global scope. Select every repository skill with `--skill '*'`; `--all` instead targets every skill and every supported agent.

At global scope, `~/.agents/skills` serves every agent except Claude Code and Hermes Agent. The `codex` target populates this shared directory; the `claude-code` target links Claude Code's directory to it. Target `hermes-agent` separately when requested.

With both default targets, non-interactive installation uses this layout:

| Scope | Shared directory | Claude Code |
| --- | --- | --- |
| Project | `.agents/skills/` | `.claude/skills/` → canonical |
| Global | `~/.agents/skills/` | `~/.claude/skills/` → canonical |

`--copy` writes independent copies. A single unique target directory also uses copy mode because no link is needed; a failed link falls back to a copy.

Global (self-created):

```bash
npx skills add ~/Coder/skills -g -a codex claude-code --skill '*' -y
```

Project-level (self-created):

```bash
npx skills add ~/Coder/skills -a codex claude-code --skill '*' -y
```

Run install/update commands automatically when the user asks to install or update skills. If scope is ambiguous, ask whether they mean global or project-level — unless context clearly indicates personal global setup.

For CLI sources, discovery, commands, and options, see [skills-cli.md](skills-cli.md).

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

   `notes` records human provenance for future upstream comparisons.

4. Copy the upstream into `skills/<skill>/SKILL.md` as the starting point and apply your changes.
5. Validate: `npx skills add ~/Coder/skills --list` must show the fork as ONE skill (the snapshot must not appear).

To update a fork from upstream — three-way compare:

- A = freshly fetched upstream (temp)
- B = `registry/upstream/<skill>/` (old pristine)
- C = `skills/<skill>/SKILL.md` (your modified copy)

Diff A↔B for the upstream delta, port the wanted parts into C, then overwrite B with A and bump `commit` / `fetched_at` / `notes` in `meta.yaml`.

## Rules

- Do not manually edit runtime install directories: `~/.agents/skills`, `~/.claude/skills`, `~/.hermes/skills`, or project `.agents/skills`.
