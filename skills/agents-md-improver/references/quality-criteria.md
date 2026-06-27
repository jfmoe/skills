# AGENTS.md Quality Criteria

Use this rubric when producing a scored AGENTS.md audit. Adapt the notes to the repository, but keep scoring consistent.

## Scoring Rubric

Total: 100 points.

| Criterion | Points | Evaluate |
| --- | ---: | --- |
| Commands/workflows | 15 | Build, test, lint, install, run, deploy, validation, and common maintenance commands are documented and current. |
| Project structure | 15 | Important directories, entry points, package boundaries, and ownership scopes are clear. |
| Agent-specific rules | 20 | Editing constraints, approvals, language, tool preferences, safety rules, and repository-specific behavior are explicit. |
| Non-obvious patterns | 15 | Generated files, quirks, gotchas, conventions, local workflows, and integration details are captured. |
| Conciseness | 10 | Content is dense, non-redundant, and avoids generic advice. |
| Currency | 15 | Instructions match current files, scripts, dependencies, and workflow reality. |
| Actionability | 10 | Rules are concrete enough for an agent to follow without guessing. |

## Grade Bands

- **A (90-100)**: Future agents can work effectively with little rediscovery. Instructions are concise, current, and scoped.
- **B (70-89)**: Useful and mostly current, with limited gaps or minor verbosity.
- **C (50-69)**: Basic guidance exists, but important workflows, constraints, or structure are missing.
- **D (30-49)**: Sparse, vague, duplicated, or stale enough to cause repeated mistakes.
- **F (0-29)**: Missing, misleading, or harmful instructions.

## Criterion Details

### Commands/workflows

Full credit requires commands that are copy-paste ready or clearly described. Include working directory requirements when commands must run from a specific path.

Flag:

- Scripts listed in package/config files but not documented
- Documented commands absent from the current repo
- Missing validation command after edits
- Missing setup or dependency install steps when nonstandard

### Project structure

Full credit requires enough structure for an agent to choose the right files before editing.

Flag:

- Monorepo package boundaries are not described
- App/library/config/generated directories are indistinguishable
- Important entry points are missing
- Nested AGENTS.md files repeat parent context but omit local scope

### Agent-specific rules

Full credit requires instructions that affect agent behavior, not just human documentation.

Flag:

- Missing rules about generated files, vendored code, lockfiles, or runtime install directories
- Missing approval gates for destructive, network, deployment, or global edits
- Conflicting language or formatting rules
- Project-specific tool preferences not documented

### Non-obvious patterns

Full credit requires durable context that is not obvious from filenames or standard tooling.

Flag:

- Hidden environment assumptions
- Local services or ports agents need to know
- Special test data, fixtures, or mocks
- Known flaky tests or required sequencing
- Generated output that must be refreshed by a specific command

### Conciseness

Full credit requires high signal per line.

Flag:

- Generic best practices
- Long prose where a command or rule would suffice
- Duplicated sections across nested files
- Session history that does not guide future work

### Currency

Full credit requires checking instructions against current repository evidence.

Flag:

- Commands that fail or reference removed tools
- File paths that no longer exist
- Architecture notes that contradict the current layout
- Rules copied from another project without adaptation

### Actionability

Full credit requires unambiguous instructions.

Flag:

- Vague statements like "follow best practices" without project-specific meaning
- Missing location, command, or condition for a rule
- Instructions that describe goals but not operational behavior

## Recommended Evidence Checks

Use lightweight repository inspection before scoring:

```bash
rg --files -g 'package.json' -g 'pnpm-lock.yaml' -g 'yarn.lock' -g 'package-lock.json' -g 'pyproject.toml' -g 'Cargo.toml' -g 'go.mod' -g 'Makefile' -g 'justfile'
```

```bash
rg -n 'scripts|test|lint|build|dev|format|typecheck|deploy' package.json pyproject.toml Makefile justfile 2>/dev/null
```

Do not over-invest in discovery for a simple AGENTS.md update. The goal is to improve agent context, not to audit the entire codebase exhaustively unless the user asks for that depth.
