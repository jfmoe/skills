---
name: hermes-agent
description: "配置、运行或排查已安装的 Hermes Agent（Nous Research 的 agent 框架）——切换其模型/提供商、编辑配置、日常运行（chat/TUI/sessions/cron/send），或修复它（更新、回滚、doctor、日志、备份）。触发词：'Hermes is broken'、'change Hermes's model'，或提及 `~/.hermes/`、`~/.local/bin/hermes`、`/Applications/Hermes.app`。不适用于首次安装、源码贡献或仅限 Windows 的问题。"
---

# Hermes Agent — 运维操作

Hermes Agent（Nous Research）已安装在本机上。本 skill 帮助你**配置、运行和排查**它。不涵盖首次安装、源码贡献或 Windows。

Hermes 迭代很快，因此容易过期的清单（子命令、提供商、配置段、斜杠命令、症状列表）**不会**被复制到这里——你在运行时现场发现它们。本 skill 只保留稳定的内容：两条硬规则、机器事实、工作流、安全规范和注意事项。

## 两条硬规则（优先级高于凭记忆回答）

**规则 1 — 不确定或未覆盖时，查阅文档。不要猜。**
本机在本地有**完整的文档集**（git 安装）——优先于网络；内容相同，可离线、可 grep。文档根目录是：

```
~/.hermes/hermes-agent/website/docs/        # 339 个 .md 文件，完整 Docusaurus 站点
```

在其中 grep/glob 找到相关指南（例如 `grep -ril <topic> ~/.hermes/hermes-agent/website/docs/`），然后阅读该文件。关键章节：`user-guide/`、`integrations/`、`reference/`、`developer-guide/`。如果本地文档缺失（非 git 安装）或仍然找不到，退回到网络索引，再从它路由到具体指南的 URL：

```
https://hermes-agent.nousresearch.com/docs/assets/files/llms-d4972c57170916efd83766ae50c3bb3d.txt
```

永远不要编造命令、标志、配置键或提供商名称。

**规则 2 — 运行前用 `--help` 核实确切的命令标志/参数。**
Hermes 的子命令和标志在版本之间会变。运行任何具体命令之前，现场检查它：

```bash
hermes <subcommand> --help        # 例如 hermes config --help, hermes auth --help
```

不要凭记忆重建标志。`--help` 输出是当前真实情况的唯一权威来源。

## 机器事实（结构稳定——用于定位）

- **主目录：** `~/.hermes/` — 配置（`config.yaml`）、密钥（`.env`）、`auth.json`、`logs/`、`sessions/`、`state.db`、`skills/`，源码在 `~/.hermes/hermes-agent/`。
- **GUI 和 CLI 共享同一个主目录。** `/Applications/Hermes.app` 和 CLI `~/.local/bin/hermes` 都运行在 `~/.hermes/` 之上。CLI 是一个轻薄的 bash 包装器，`exec` 到 `~/.hermes/hermes-agent/venv/bin/hermes`。**任何配置/认证改动同时影响 GUI 和 CLI。** 不存在按界面分开的配置。
- **源码安装：** `.install_method=git`（文件 `~/.hermes/.install_method`），源码在 `~/.hermes/hermes-agent/`。官方更新走 `hermes update`，它可以做更新前备份（见 `hermes update --help`；由 `updates.pre_update_backup` 控制，本机默认关闭）。不要假设固定的备份路径——按 `reference/troubleshooting.md` 定位备份。
- **完整文档在本地：** `~/.hermes/hermes-agent/website/docs/` 保存完整的 Docusaurus 文档站点（339 个 `.md` 文件）。优先于网络。`hermes update` 会替换源码目录，但这个相对路径保持稳定。
- Hermes 自带的捆绑运维 skill 的本地副本位于 `~/.hermes/skills/autonomous-ai-agents/hermes-agent/SKILL.md`——可作为更完整（但清单繁重、过期更快）的参考。它的清单正是本 skill 要绕开的东西；把它**稳定**的指导（安全、注意事项）视为与下面的规则一致。

## 路由——意图 → 参考文件 + 发现命令

| 你想…… | 阅读 | 用以下命令发现当前真相 |
|---|---|---|
| 配置 / 切换提供商或模型、编辑任何配置 | `reference/config-editing.md` | `~/.hermes/config.yaml` 或 `hermes config show`；`hermes model`；`hermes config --help`、`hermes auth --help` |
| 日常运行 / 使用（chat、TUI、sessions、cron、send） | `reference/operations.md` | `hermes --help`；`hermes <cmd> --help`；会话内 `/help` |
| 诊断 / 维护 / 更新 / 回滚 | `reference/troubleshooting.md` | `hermes doctor`、`hermes status`、`hermes logs` |

**发现命令（当前存在什么，永不复制进本 skill）：**

- 子命令：`hermes --help`，然后用 `hermes <cmd> --help` 查看标志。
- 配置：直接读 `~/.hermes/config.yaml`，或 `hermes config show`；路径通过 `hermes config path` / `hermes config env-path`。
- 工具：`hermes tools list`。Skills：`hermes skills list`。提供商/模型：`hermes model`。
- 会话内斜杠命令：`/help`。
- 任何更深入或未覆盖的内容：**规则 1**——grep 本地文档 `~/.hermes/hermes-agent/website/docs/`（完整离线文档集），网络索引仅作后备。

## 安全规范（与 Hermes 捆绑的 autonomous-ai-agents skill 一致）

这些直接采纳自 Hermes 自己的运维 skill——不要另造一套。完整的编辑规范（专用 `config`/`auth` 命令、配置与 `.env` 分离、验证）在 `reference/config-editing.md` 中；以下是最基本的入口要点：

- **密钥：** API 密钥走 `hermes auth`，不要手工编辑 `.env`。永远不以明文打印密钥，也绝不把它们提交到任何仓库。
- **`security.redact_secrets` 默认开启**，并在进程启动时快照——会话中途切换它不会生效（需要重启）。这是有意设计，防止 LLM 在任务中途对自己关闭脱敏。
- **命令审批（`approvals.mode`）：** `manual`（默认——破坏性命令前提示）/ `smart` / `off`（等价于 `--yolo`）。YOLO / `off` 不会禁用密钥脱敏；两者相互独立。在 `manual` 环境中，破坏性操作前要确认。
- **改动需要重启才生效**——完整映射（tool/skill → `/reset`，config → `/restart` 或重新启动）见 `reference/troubleshooting.md`。
