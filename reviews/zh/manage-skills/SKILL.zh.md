---
name: manage-skills
description: 当用户要求创建、编辑、安装、更新、同步、列出或派生（fork）个人 skill 时使用。
---

# 管理 Skills

个人 skill 源仓库：`~/Coder/skills`（远端 `https://github.com/jfmoe/skills`）。所有源码编辑都在此进行；绝不手工编辑运行时安装目录。

## 仓库准备

在操作 skills 之前，确保源仓库存在且为最新：

1. 如果 `~/Coder/skills` 不存在，克隆它：

```bash
git clone https://github.com/jfmoe/skills ~/Coder/skills
```

2. 如果存在本地改动，不要 pull。继续使用本地内容，并报告脏状态。
3. 如果该路径存在但不是 git 仓库，不要覆盖它；停止并报告。

## 仓库布局

```text
skills/                 可安装的 skills（原样复制到项目中）
  <skill>/              每个 skill 一个文件夹——扁平结构，无分类目录
registry/
  upstream/<skill>/     fork 的纯净上游快照与来源信息
```

- 仓库管理的 skills 分两类：**original**（自建）和 **fork**（修改过的第三方——见"派生第三方 Skill"）。未修改的第三方 skills 留在本仓库之外。

## 创建或编辑 Skill

仅在用户创建或修改 skill 时才编辑 `~/Coder/skills/skills/<skill>/SKILL.md`。

创建或编辑后，运行只读校验：

```bash
npx skills add ~/Coder/skills --list
```

## 中文审查镜像

英文撰写的 skill 在 `reviews/zh/<skill>/` 下有一份中文审查镜像，复刻源目录结构：`SKILL.md` 变为 `SKILL.zh.md`（仓库中任何字面名为 `SKILL.md` 的文件都会被注册为可安装）；其他文件保持原名。中文撰写的 skills 没有镜像。

- 镜像是纯翻译——不加标注或来源头。从源码重新生成；绝不手工编辑。
- 创建或编辑英文 skill 的 `.md` 文件后，在同一提交中重新生成其镜像文件。编辑后的 `--list` 校验必须显示不变的 skill 集合。
- 以中文给出的审查反馈会应用到英文源文件上；源文件保持为准。

## 安装与同步

明确指名的单个 agent 是私有目标：验证其原生 skill 目录，且只安装到那里。绝不回退到项目级或全局的 `.agents/skills`；那些只用于共享的多 agent 安装或明确请求。如果原生目标未知，停止并报告。

当用户未指名 agent 时，默认目标为 `-a codex claude-code`。项目作用域是 CLI 默认值；`-g` 选择全局作用域。用 `--skill '*'` 选择所有仓库 skills；`--all` 则面向所有 skills 和所有受支持的 agents。

在全局作用域下，`~/.agents/skills` 服务于除 Claude Code 和 Hermes Agent 之外的所有 agent。`codex` 目标填充该共享目录；`claude-code` 目标将 Claude Code 的目录链接到它。需要时单独指定 `hermes-agent` 目标。

使用两个默认目标时，非交互安装采用如下布局：

| 作用域 | 共享目录 | Claude Code |
| --- | --- | --- |
| 项目 | `.agents/skills/` | `.claude/skills/` → 规范目录 |
| 全局 | `~/.agents/skills/` | `~/.claude/skills/` → 规范目录 |

`--copy` 写入独立副本。单个唯一目标目录也使用复制模式，因为不需要链接；链接失败时回退为复制。

全局（自建）：

```bash
npx skills add ~/Coder/skills -g -a codex claude-code --skill '*' -y
```

项目级（自建）：

```bash
npx skills add ~/Coder/skills -a codex claude-code --skill '*' -y
```

当用户要求安装或更新 skills 时，自动运行安装/更新命令。如果作用域含糊，询问用户是指全局还是项目级——除非上下文明确表明是个人全局配置。

关于 CLI 来源、发现、命令和选项，见 [skills-cli.md](skills-cli.md)。

## 派生第三方 Skill

fork 是你修改过的第三方 skill。保留两份副本——一份干净的可安装副本和一份用于 diff 的纯净快照。

创建 fork：

1. 将上游 skill 拉取到临时目录，记录其 `ref` 和 `commit`。
2. 将纯净文件保存到 `registry/upstream/<skill>/`。**将每个 `SKILL.md` 重命名为 `SKILL.md.orig`**——`npx skills` 会把仓库中任何字面名为 `SKILL.md` 的文件注册为可安装（已验证；没有忽略选项）。其他文件保持原样。
3. 编写 `registry/upstream/<skill>/meta.yaml`。这是规范的 `meta.yaml` schema：

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

   `notes` 记录供未来上游对比使用的人类可读来源信息。

4. 将上游内容复制到 `skills/<skill>/SKILL.md` 作为起点，并应用你的修改。
5. 校验：`npx skills add ~/Coder/skills --list` 必须将该 fork 显示为一个 skill（快照不得出现）。

从上游更新 fork——三方对比：

- A = 新拉取的上游（临时）
- B = `registry/upstream/<skill>/`（旧纯净快照）
- C = `skills/<skill>/SKILL.md`（你修改过的副本）

对 A↔B 做 diff 得到上游变更，将需要的部分移植到 C，然后用 A 覆盖 B，并在 `meta.yaml` 中更新 `commit` / `fetched_at` / `notes`。

## 规则

- 不要手工编辑运行时安装目录：`~/.agents/skills`、`~/.claude/skills`、`~/.hermes/skills`，或项目的 `.agents/skills`。
