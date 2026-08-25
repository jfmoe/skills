# skills CLI Reference

This file covers CLI behavior.

## Sources and discovery

`<source>` accepts more than GitHub shorthand:

```bash
# GitHub repository or a skill subdirectory
npx skills add owner/repo
npx skills add https://github.com/owner/repo/tree/main/skills/example

# GitLab, another Git host, or a local directory
npx skills add https://gitlab.com/org/repo
npx skills add git@example.com:org/repo.git
npx skills add ./local-skills

# A directly downloadable SKILL.md or supported archive
npx skills add https://example.com/download/my-skill
```

Direct downloads may contain one valid `SKILL.md` or a `.zip`, `.tar`, `.tar.gz`, or `.tgz` archive. Defaults limit the download to 10 MiB, extracted content to 25 MiB, and archives to 1000 files. Raise `SKILLS_DOWNLOAD_MAX_BYTES`, `SKILLS_EXTRACT_MAX_BYTES`, or `SKILLS_EXTRACT_MAX_FILES` only for a trusted source.

Private sources use existing Git, GitHub CLI, or SSH authentication. `GITHUB_TOKEN` and `GH_TOKEN` are optional explicit credentials for GitHub API access; a working `gh` login does not require exporting its token.

Default discovery checks a root `SKILL.md`, known skill containers, and declared Claude plugin manifests. Known containers are walked to a bounded depth; a shallower `SKILL.md` shadows nested ones. If standard discovery finds nothing, the CLI falls back to a recursive search. `--full-depth` requests recursive discovery deliberately.

The CLI supports nested catalogs, but this repository does not: installable skills stay flat at `skills/<skill>/SKILL.md`. Validate the exposed set without installing:

```bash
npx skills add ~/Coder/skills --list
```

Skills with `metadata.internal: true` are hidden unless `INSTALL_INTERNAL_SKILLS=1` is set.

## `add` — install or synchronize

```bash
npx skills add <source> [options]
```

| Option | Meaning |
| --- | --- |
| `-g, --global` | Install at user level instead of project level |
| `-a, --agent <agents...>` | Target agents; `'*'` selects all agents |
| `-s, --skill <skills...>` | Target skills; `'*'` selects all skills |
| `-l, --list` | List discoverable skills without installing |
| `-y, --yes` | Skip confirmation prompts |
| `--copy` | Copy independently to target directories |
| `--all` | Select all skills and all agents, then skip prompts |
| `--full-depth` | Use recursive discovery |
| `--metadata <json>` | Attach valid JSON to the install telemetry event |
| `--subagent <names...>` | Install to Eve subagents; `root` targets Eve's root agent |

Repository recipes:

```bash
# Install or synchronize all repository skills globally
npx skills add ~/Coder/skills -g -a codex claude-code --skill '*' -y

# Install or synchronize all repository skills in the current project
npx skills add ~/Coder/skills -a codex claude-code --skill '*' -y

# Install one repository skill globally
npx skills add ~/Coder/skills -g -a codex claude-code --skill manage-skills -y

# Shared global directory (~/.agents/skills)
npx skills add ~/Coder/skills -g -a codex --skill '*' -y

# One third-party skill
npx skills add vercel-labs/agent-skills -g -a codex claude-code \
  --skill web-design-guidelines -y
```

Repeated `--agent` / `--skill` flags and space-separated values are both accepted by the current CLI. Quote `'*'` so the shell does not expand it.

## `use` — run one skill without installing

`use` resolves and downloads a source like `add`, then generates a prompt for exactly one skill in a temporary directory.

```bash
# Print only the generated prompt to stdout
npx skills use vercel-labs/agent-skills@web-design-guidelines
npx skills use vercel-labs/agent-skills --skill web-design-guidelines

# Pipe the prompt or launch one supported agent interactively
npx skills use vercel-labs/agent-skills@web-design-guidelines | claude
npx skills use vercel-labs/agent-skills --skill web-design-guidelines \
  --agent claude-code
```

Options are `-s, --skill <skill>`, `-a, --agent <agent>`, and `--full-depth`. Without `--agent`, stdout contains only the prompt so piping remains safe.

## Installed-skill commands

### `list`, `ls`

The current CLI help defines project scope as the default; `-g` selects global scope.

```bash
npx skills list
npx skills ls -g
npx skills ls -a claude-code codex
npx skills ls --json
```

`--json` emits machine-readable output without ANSI codes.

### `remove`, `rm`

```bash
npx skills remove [skills...] [options]

npx skills remove                         # interactive
npx skills remove skill-a skill-b -y
npx skills rm -g -a claude-code manage-skills -y
npx skills remove --skill '*' -a cursor   # all skills from one agent
npx skills remove --all                   # every installed skill; -y implied
```

Use `-g` for global scope, `-a` to limit agents, `-s` as an alternative to positional skill names, and `-y` to skip prompts. `--all` cannot be combined with named skills.

### `update`, `upgrade`

```bash
npx skills update [skills...] [options]

npx skills update                 # interactive scope prompt
npx skills update my-skill
npx skills update skill-a skill-b
npx skills update -g              # global only
npx skills update -p              # project only
npx skills update -y              # infer project scope in a project, else global
```

`update` follows each installed skill's recorded source. Updating a fork's source copy and pristine snapshot is a separate repository workflow defined in [`SKILL.md`](SKILL.md#forking-a-third-party-skill).

## Discovery and scaffolding commands

```bash
npx skills find                   # interactive registry search
npx skills find typescript        # keyword search
npx skills find react --owner vercel

npx skills init                   # create ./SKILL.md
npx skills init my-skill          # create ./my-skill/SKILL.md
```

`init` uses its argument as both directory and frontmatter name. In this repository, create `skills/<skill>/SKILL.md` through the `manage-skills` workflow instead; passing `skills/<skill>` to `init` would produce an invalid slash-containing name.

## Experimental commands

```bash
npx skills experimental_install
npx skills experimental_sync [-a <agents...>] [-y]
```

`experimental_install` restores from `skills-lock.json`. `experimental_sync` discovers skills in `node_modules` and synchronizes them into agent directories. Treat both as unstable CLI surfaces and check `--help` before using them.

## Environment controls

| Variable | Effect |
| --- | --- |
| `INSTALL_INTERNAL_SKILLS=1` | Include skills marked `metadata.internal: true` |
| `DISABLE_TELEMETRY=1` | Disable anonymous usage telemetry |
| `DO_NOT_TRACK=1` | Alternative telemetry opt-out |
| `GITHUB_TOKEN`, `GH_TOKEN` | Explicit GitHub API credentials |
