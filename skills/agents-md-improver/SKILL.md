---
name: agents-md-improver
description: Manual-only.
---

# AGENTS.md Improver

Audit, evaluate, and improve AGENTS.md instruction files so future agent sessions have concise, current, actionable project context.

This skill is manual-only. Use it only when the user explicitly asks for `agents-md-improver` or directly asks to run this skill.

This skill can write to AGENTS.md files only after presenting a quality report or proposed additions and receiving explicit user approval.

## Modes

- **Audit mode**: inspect AGENTS.md files, score quality, propose targeted updates, then apply approved changes.
- **Session-learning mode**: review the current session for durable learnings, propose brief AGENTS.md additions, then apply approved changes.

## Phase 1: Discovery

Find relevant agent instruction files.

For the current repository:

```bash
find . \( -name "AGENTS.md" -o -name ".agents.md" \) -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -50
```

For explicitly requested global or external locations, inspect only the paths the user named. Common global candidates include:

- `~/.agents/AGENTS.md`
- `~/.codex/AGENTS.md`
- `~/.claude/CLAUDE.md` when the user is intentionally bridging Claude-style instructions
- Other user-specified agent instruction files

Do not silently edit global files. Global files require explicit user intent and approval.

## File Types and Placement

| Type            | Location                                                                  | Purpose                                                                |
| --------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Project root    | `./AGENTS.md`                                                             | Shared repository instructions and project-wide rules                  |
| Nested scope    | `./packages/*/AGENTS.md`, `./apps/*/AGENTS.md`, or any nested `AGENTS.md` | Directory-specific instructions that override or refine parent context |
| Local/private   | `./.agents.md` or a user-specified local file                             | Personal or local-only instructions, usually gitignored                |
| Global defaults | User-specified global paths                                               | Cross-project preferences and durable agent defaults                   |

When multiple files exist, place each addition at the narrowest scope where it remains useful.

## Phase 2: Quality Assessment

For each file, evaluate whether it helps an agent act correctly with minimal extra discovery. Read [references/quality-criteria.md](references/quality-criteria.md) when doing a scored audit.

Quick checklist:

| Criterion              | Weight | Check                                                                                     |
| ---------------------- | ------ | ----------------------------------------------------------------------------------------- |
| Commands and workflows | High   | Are build, test, lint, deploy, install, and validation commands documented when relevant? |
| Project structure      | High   | Can an agent understand important directories, entry points, and ownership boundaries?    |
| Agent-specific rules   | High   | Are constraints about edits, approvals, tools, language, style, and safety clear?         |
| Non-obvious patterns   | Medium | Are gotchas, conventions, generated files, and integration quirks captured?               |
| Conciseness            | Medium | Is the file dense and useful without generic advice or obvious restatements?              |
| Currency               | High   | Does it match the current repository and tooling?                                         |
| Actionability          | High   | Are instructions concrete, executable, and scoped?                                        |

Quality grades:

- **A (90-100)**: Comprehensive, current, concise, and actionable
- **B (70-89)**: Good coverage with minor gaps
- **C (50-69)**: Basic guidance but missing important details
- **D (30-49)**: Sparse, vague, or noticeably stale
- **F (0-29)**: Missing, misleading, or severely outdated

## Phase 3: Quality Report

Always output the report before editing files.

Use this format:

```markdown
## AGENTS.md Quality Report

### Summary

- Files found: X
- Average score: X/100
- Files needing update: X

### File-by-File Assessment

#### 1. ./AGENTS.md (Project Root)

**Score: XX/100 (Grade: X)**

| Criterion            | Score | Notes |
| -------------------- | ----- | ----- |
| Commands/workflows   | X/15  | ...   |
| Project structure    | X/15  | ...   |
| Agent-specific rules | X/20  | ...   |
| Non-obvious patterns | X/15  | ...   |
| Conciseness          | X/10  | ...   |
| Currency             | X/15  | ...   |
| Actionability        | X/10  | ...   |

**Issues:**

- ...

**Recommended additions:**

- ...
```

## Phase 4: Targeted Updates

After the report, ask whether the user wants changes. Before editing, show proposed changes as diffs or quoted blocks.

Update guidelines:

1. Add only durable, project-specific information.
2. Prefer one line per concept when possible.
3. Keep instructions scoped to the file's location.
4. Preserve existing structure and tone.
5. Avoid duplicating parent instructions in nested files unless the repeated rule prevents real mistakes.

Avoid adding:

- Generic best practices an agent already knows
- Obvious facts visible from filenames alone
- One-off session details unlikely to recur
- Large explanations where a command or short rule is enough
- Tool or workflow rules that conflict with higher-priority user or system instructions

Diff format:

````markdown
### Update: ./AGENTS.md

**Why:** Build validation was missing, so future agents would not know the expected check.

````diff
+ ## Validation
+
+ ```bash
+ npm test
+ ```
````
````

## Phase 5: Apply Approved Updates

Apply only the changes the user approved. Preserve existing content and avoid unrelated rewrites.

After editing:

1. Re-read the changed section to verify placement and formatting.
2. Run a lightweight validation when available, such as Markdown formatting checks or the project's documented validation command.
3. Summarize files changed and any validation that could not be run.

## Session-Learning Mode

Use this mode when the user asks to revise AGENTS.md from the current session.

### Step 1: Reflect

Identify durable context that would have helped future agents:

- Commands that were discovered or verified
- Code style or repository conventions that were followed
- Testing or validation approaches that worked
- Environment, tooling, permissions, or configuration quirks
- Warnings, generated files, or areas agents should avoid editing
- Approval gates or human workflow preferences

### Step 2: Find Target Files

Find repository files first:

```bash
find . \( -name "AGENTS.md" -o -name ".agents.md" \) -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -20
```

Use global files only when the user explicitly asks for global instruction updates.

### Step 3: Draft Additions

Keep additions concise. Preferred format:

```text
<command, rule, or pattern> - <brief reason or usage>
```

Choose the narrowest file that benefits from the learning.

### Step 4: Show Proposed Changes

For each addition, show:

- Target file
- One-line reason
- Diff or quoted block

Ask for approval before editing.

### Step 5: Apply with Approval

Only edit files the user approved.

## Templates

Read [references/templates.md](references/templates.md) when creating a missing AGENTS.md or when a file needs substantial restructuring.

## Common Issues to Flag

1. Stale commands that no longer exist or do not match package scripts
2. Missing validation or test instructions
3. Missing repository-specific edit constraints
4. Unclear ownership boundaries in monorepos
5. Nested instructions that duplicate parent files without adding local value
6. Conflicting instructions between parent and nested files
7. Long generic sections that consume prompt space without guiding action
8. Unmarked generated or vendor files that agents might accidentally edit
9. Global preferences placed in project files, or project-specific rules placed globally

## What Makes a Great AGENTS.md

- Concise and readable
- Current with the repository's actual commands and structure
- Specific about what agents should do, avoid, ask, and verify
- Scoped to the directory where it lives
- Focused on recurring context, not one-off history
- Written as instructions, not commentary
