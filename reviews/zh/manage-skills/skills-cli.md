# skills CLI 参考

本文件涵盖 CLI 行为。

## 来源与发现

`<source>` 接受的不只是 GitHub 简写：

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

直接下载可以包含一个有效的 `SKILL.md`，或一个 `.zip`、`.tar`、`.tar.gz`、`.tgz` 归档。默认限制下载为 10 MiB、解压内容为 25 MiB、归档为 1000 个文件。仅对可信来源才提高 `SKILLS_DOWNLOAD_MAX_BYTES`、`SKILLS_EXTRACT_MAX_BYTES` 或 `SKILLS_EXTRACT_MAX_FILES`。

私有来源使用现有的 Git、GitHub CLI 或 SSH 认证。`GITHUB_TOKEN` 和 `GH_TOKEN` 是可选的显式 GitHub API 凭据；正常工作的 `gh` 登录不需要导出其 token。

默认发现会检查根目录的 `SKILL.md`、已知的 skill 容器，以及声明的 Claude 插件清单。已知容器按有界深度遍历；较浅的 `SKILL.md` 会遮蔽嵌套的同名文件。如果标准发现一无所获，CLI 回退为递归搜索。`--full-depth` 显式要求递归发现。

CLI 支持嵌套目录，但本仓库不支持：可安装 skills 保持扁平地位于 `skills/<skill>/SKILL.md`。不安装即可校验暴露的集合：

```bash
npx skills add ~/Coder/skills --list
```

带 `metadata.internal: true` 的 skills 会被隐藏，除非设置 `INSTALL_INTERNAL_SKILLS=1`。

## `add` — 安装或同步

```bash
npx skills add <source> [options]
```

| 选项 | 含义 |
| --- | --- |
| `-g, --global` | 安装到用户级而非项目级 |
| `-a, --agent <agents...>` | 目标 agents；`'*'` 选择所有 agents |
| `-s, --skill <skills...>` | 目标 skills；`'*'` 选择所有 skills |
| `-l, --list` | 列出可发现的 skills 而不安装 |
| `-y, --yes` | 跳过确认提示 |
| `--copy` | 独立复制到目标目录 |
| `--all` | 选择所有 skills 和所有 agents，然后跳过提示 |
| `--full-depth` | 使用递归发现 |
| `--metadata <json>` | 将合法 JSON 附加到安装遥测事件 |
| `--subagent <names...>` | 安装到 Eve subagents；`root` 指向 Eve 的根 agent |

仓库常用命令：

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

当前 CLI 同时接受重复的 `--agent` / `--skill` 标志和空格分隔的值。给 `'*'` 加引号，避免 shell 展开。

## `use` — 不安装直接运行一个 skill

`use` 像 `add` 一样解析并下载来源，然后在临时目录中为恰好一个 skill 生成提示词。

```bash
# Print only the generated prompt to stdout
npx skills use vercel-labs/agent-skills@web-design-guidelines
npx skills use vercel-labs/agent-skills --skill web-design-guidelines

# Pipe the prompt or launch one supported agent interactively
npx skills use vercel-labs/agent-skills@web-design-guidelines | claude
npx skills use vercel-labs/agent-skills --skill web-design-guidelines \
  --agent claude-code
```

选项为 `-s, --skill <skill>`、`-a, --agent <agent>` 和 `--full-depth`。不带 `--agent` 时，stdout 只包含提示词，因此管道是安全的。

## 已安装 skill 的命令

### `list`、`ls`

当前 CLI 帮助将项目作用域定义为默认；`-g` 选择全局作用域。

```bash
npx skills list
npx skills ls -g
npx skills ls -a claude-code codex
npx skills ls --json
```

`--json` 输出不含 ANSI 代码的机器可读结果。

### `remove`、`rm`

```bash
npx skills remove [skills...] [options]

npx skills remove                         # interactive
npx skills remove skill-a skill-b -y
npx skills rm -g -a claude-code manage-skills -y
npx skills remove --skill '*' -a cursor   # all skills from one agent
npx skills remove --all                   # every installed skill; -y implied
```

使用 `-g` 表示全局作用域，`-a` 限定 agents，`-s` 作为位置参数 skill 名的替代，`-y` 跳过提示。`--all` 不能与指名 skills 组合。

### `update`、`upgrade`

```bash
npx skills update [skills...] [options]

npx skills update                 # interactive scope prompt
npx skills update my-skill
npx skills update skill-a skill-b
npx skills update -g              # global only
npx skills update -p              # project only
npx skills update -y              # infer project scope in a project, else global
```

`update` 遵循每个已安装 skill 记录的来源。更新 fork 的源码副本和纯净快照是 [`SKILL.md`](SKILL.md#forking-a-third-party-skill) 中定义的独立仓库工作流。

## 发现与脚手架命令

```bash
npx skills find                   # interactive registry search
npx skills find typescript        # keyword search
npx skills find react --owner vercel

npx skills init                   # create ./SKILL.md
npx skills init my-skill          # create ./my-skill/SKILL.md
```

`init` 将其参数同时用作目录名和 frontmatter 名称。在本仓库中，应通过 `manage-skills` 工作流创建 `skills/<skill>/SKILL.md`；将 `skills/<skill>` 传给 `init` 会产生含斜杠的非法名称。

## 实验性命令

```bash
npx skills experimental_install
npx skills experimental_sync [-a <agents...>] [-y]
```

`experimental_install` 从 `skills-lock.json` 恢复。`experimental_sync` 发现 `node_modules` 中的 skills 并同步到 agent 目录。两者都应视为不稳定的 CLI 界面，使用前检查 `--help`。

## 环境变量控制

| 变量 | 效果 |
| --- | --- |
| `INSTALL_INTERNAL_SKILLS=1` | 包含标记为 `metadata.internal: true` 的 skills |
| `DISABLE_TELEMETRY=1` | 禁用匿名使用遥测 |
| `DO_NOT_TRACK=1` | 另一种遥测退出方式 |
| `GITHUB_TOKEN`、`GH_TOKEN` | 显式 GitHub API 凭据 |
