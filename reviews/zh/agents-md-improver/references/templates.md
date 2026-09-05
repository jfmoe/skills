# AGENTS.md 模板

创建缺失的 AGENTS.md 或对质量较差的文件进行实质性重构时使用这些模板。只保留与仓库相关的章节。

## 通用项目模板

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

## 代码仓库模板

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

## Monorepo 根模板

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

## 嵌套包模板

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

## 会话学习新增内容模板

工作会话之后的小型更新使用此模板：

```markdown
- `command-or-pattern` - Durable reason this helps future agents.
```

示例：

```markdown
- `npx skills add ~/Coder/skills --list` - Read-only validation for local skill source edits.
- Do not edit `dist/` directly; regenerate it with `npm run build`.
- Check nested `AGENTS.md` files before changing files under `packages/`.
```

## 放置指导

- 将仓库级规则放在根目录的 AGENTS.md 中。
- 将包特定的命令和怪癖放在嵌套的 AGENTS.md 文件中。
- 仅在用户要求时，将个人偏好放在本地或全局文件中。
- 不要将完整的根模板复制到每个嵌套文件中。
