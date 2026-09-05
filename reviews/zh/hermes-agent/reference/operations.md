# 日常运维操作

稳定的运行**模式**。确切的标志和完整子命令清单会过期——运行前用 `hermes <cmd> --help` 确认（SKILL.md 规则 2），用 `hermes --help` 发现当前存在什么。未覆盖的内容，获取文档索引（规则 1）。

## 运行它

- **交互式（默认）：** `hermes` 直接进入聊天。用 `hermes chat --tui` 或 `hermes chat --cli` 强制指定界面。
- **一次性 / 可脚本化：** `hermes chat -q "…"` 非交互地运行单个查询。顶层 `hermes -z "…"`（`--oneshot`）只打印最终响应文本（无 banner/spinner/工具预览）——用于管道和脚本；此模式下审批会被自动绕过，请按此对待。
- **继续对话：** `--continue`（最近的，或按名称）/ `--resume <session-id>`。这些是标志，不是子命令——确切形式见 `hermes chat --help`。
- **GUI / 桌面应用：** `hermes desktop`（别名 `hermes gui`）构建并启动 Electron 应用。它与 CLI 共享同一个 `~/.hermes/` 主目录。

## 会话

`hermes sessions` 管理会话存储（列出、浏览、重命名、导出、清理、删除、统计）。子命令及其标志会变——运行 `hermes sessions --help`。会话内，`/resume`、`/branch` 和历史命令可通过 `/help` 查看。

## 自动化

- **定时任务：** `hermes cron`（create/list/edit/pause/resume/run/remove）。计划接受时长（`30m`）、"every" 短语、5 字段 cron 表达式或 ISO 时间戳。`hermes cron --help`，然后看具体子命令的 `--help`。周期性工作优先用 cron 而不是派生进程——它处理投递和重试。
- **向已配置的平台发送消息**（从脚本/cron/CI，无 agent 循环）：`hermes send`——复用 gateway 的平台凭据。`hermes send --list` 显示可用目标；目标语法见 `hermes send --help`（`platform`、`platform:chat_id`、`platform:#channel`）。

## 会话内斜杠命令

在聊天会话中输入 `/help` 获取当前的权威列表——这里没有复制，因为新命令经常加入。（少数几个在本 skill 的工作流中反复出现：`/reset` 开新会话，`/restart` 重启 gateway。）

## 更深入的领域（一行指引——不在此展开）

这些存在且强大，但超出本 skill 的日常范围。真正需要时，从文档索引获取它的指南（规则 1）：

- **多实例 / tmux 编排** 和 **`delegate_task`**，用于并行或长时间运行的 agent。
- **delegation**、**curator**（后台 skill 维护）和 **kanban**（多 agent 工作队列）子系统。
- **MCP servers**、**plugins**、**profiles**、**webhooks** 和 **gateway** 平台设置。

本地捆绑 skill `~/.hermes/skills/autonomous-ai-agents/hermes-agent/SKILL.md` 有关于派生 agent 和 tmux 编排的可运行示例，需要起点时可以参考。
