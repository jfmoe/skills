# skills CLI Reference

Invoke as `npx skills <command> [options]`. A `<source>` package is either a local path (`~/Coder/skills`) or a remote repo (`vercel-labs/agent-skills`, `https://github.com/vercel-labs/agent-skills`).

Repo conventions:

- Default agent target is `claude-code` (`-a claude-code`); Cursor reads `~/.agents/skills` automatically, so it needs no separate target.
- Let the CLI manage symlinks into runtime dirs; never hand-edit `~/.agents/skills`, `~/.claude/skills`, `~/.cursor/skills`, or project `.agents/skills`.
- `<source>` for self-created skills is always `~/Coder/skills`.

## add — install or sync skills

```bash
npx skills add <source> [options]
```

| Option | Meaning |
| --- | --- |
| `-g, --global` | Install at user level instead of project level |
| `-a, --agent <agents>` | Target agents; `'*'` for all |
| `-s, --skill <skills>` | Target skills; `'*'` for all |
| `-l, --list` | List available skills in the source without installing |
| `-y, --yes` | Skip confirmation prompts |
| `--copy` | Copy files instead of symlinking |
| `--all` | Shorthand for `--skill '*' --agent '*' -y` |
| `--full-depth` | Search all subdirectories even when a root SKILL.md exists |

Common uses:

```bash
# Read-only validation: list skills the source exposes
npx skills add ~/Coder/skills --list

# Install all self-created skills globally
npx skills add ~/Coder/skills -g -a claude-code --skill '*' -y

# Install all self-created skills into the current project
npx skills add ~/Coder/skills -a claude-code --skill '*' -y

# Install a single self-created skill globally
npx skills add ~/Coder/skills -g -a claude-code --skill manage-skills -y

# Install a third-party skill globally (then record it in registry/third-party.md)
npx skills add vercel-labs/agent-skills -g -a claude-code --skill pr-review -y
```

## list / ls — list installed skills

```bash
npx skills list [options]
```

| Option | Meaning |
| --- | --- |
| `-g, --global` | List global skills (default: project) |
| `-a, --agent <agents>` | Filter by agent |
| `--json` | Machine-readable JSON output |

```bash
npx skills ls -g                 # global installed skills
npx skills ls -a claude-code     # filter by agent
npx skills ls --json             # JSON output
```

## remove / rm — uninstall skills

```bash
npx skills remove [skills] [options]
```

| Option | Meaning |
| --- | --- |
| `-g, --global` | Remove from global scope |
| `-a, --agent <agents>` | Remove from specific agents; `'*'` for all |
| `-s, --skill <skills>` | Skills to remove; `'*'` for all |
| `-y, --yes` | Skip confirmation prompts |
| `--all` | Shorthand for `--skill '*' --agent '*' -y` |

```bash
npx skills remove                       # interactive
npx skills remove web-design            # by name
npx skills rm -g -a claude-code --skill manage-skills -y
```

If a removed skill was a global third-party skill, also delete its row from `registry/third-party.md`.

## update / upgrade — update to latest

```bash
npx skills update [skills...] [options]
```

| Option | Meaning |
| --- | --- |
| `-g, --global` | Update global skills only |
| `-p, --project` | Update project skills only |
| `-y, --yes` | Skip scope prompt (auto-detects project, else global) |

```bash
npx skills update            # update everything in scope
npx skills update my-skill   # update a single skill
npx skills update -g         # global only
```

## find — search the public registry

```bash
npx skills find [query]
```

```bash
npx skills find              # interactive
npx skills find typescript   # by keyword
```

## init — scaffold a new skill

```bash
npx skills init <name>       # creates <name>/SKILL.md
```

Prefer creating self-created skills directly under `skills/<category>/<skill>/SKILL.md` in this repo instead of `init`, unless a quick scaffold is wanted.

## experimental commands

```bash
npx skills experimental_install        # restore from skills-lock.json
npx skills experimental_sync [-a <agents>] [-y]   # sync from node_modules into agent dirs
```
