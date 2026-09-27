---
name: hermes-agent
description: "本机部署了 Hermes Agent（Nous Research）。当任务涉及 Hermes——使用、配置、更新或排查它——或涉及 `~/.hermes/` 时使用。"
---

# Hermes Agent

Hermes Agent 以 git 方式安装在本机。本 skill 给出它的目录布局、查阅资料的位置和本地维护规则。Hermes 迭代很快：命令、参数、配置键和提供商以下列来源为准，不要凭记忆。

## 布局

- **Home：** `~/.hermes/`——`config.yaml`（设置）、`.env`（密钥）、`auth.json`、`state.db`、`logs/`、`skills/`、`SOUL.md`。设置了 `$HERMES_HOME` 时，由它替代 `~/.hermes`。
- **源码：** `~/.hermes/hermes-agent/`，是 `NousResearch/hermes-agent` 的 git checkout。
- **入口：** CLI `~/.local/bin/hermes`（进入源码安装的启动脚本）、由 `hermes desktop` 从源码构建的桌面应用（`~/.hermes/hermes-agent/apps/desktop/release/mac-arm64/Hermes.app`），以及由 launchd 托管的消息网关（`ai.hermes.gateway`）。三者共用同一个 home，因此配置或凭据的改动会同时影响它们。

## 查阅位置

1. **内置 skill：** `~/.hermes/hermes-agent/skills/autonomous-ai-agents/hermes-agent/SKILL.md`。由上游维护，`hermes update` 会刷新它。先读它；它的路由表为每个主题指向一个参考文件。
2. **本地文档：** `~/.hermes/hermes-agent/website/docs/`，完整的文档站点。用 grep 检索。
3. **Web 索引：** `https://hermes-agent.nousresearch.com/docs/llms.txt`，每个已文档化的功能一行。本地文档无法回答时使用。
4. **CLI 帮助：** `hermes --help` 和 `hermes <command> --help` 给出已安装版本的命令和参数。运行命令前先查看。

## 维护规则

- **源码树只读。** 通过 CLI、`config.yaml`、`.env` 和 `~/.hermes/skills/` 修改 Hermes。只用 `hermes update` 更新；用 `hermes update --plan` 预览。
- **设置与密钥分开。** 用 `hermes config set KEY VAL` 修改设置；用 `hermes auth` 添加凭据。`.env` 只存放密钥。不要打印或提交密钥值。
- **只用自己的登录。** 保持 `auth.adopt_external_logins: false`。Hermes 只使用自己的登录（`hermes auth add <provider>`），因此永远不会刷新 Claude Code 或 Codex CLI 的登录。
- **先用内置工具备份。** 每种工具会自行清理旧副本，因此不要添加带日期的 `.bak` 文件。
  - `config.yaml`：Hermes 会自动在 `backups/config/` 中保留副本。
  - `.env`、`auth.json`、cron 及其他状态：运行 `hermes backup --quick --label <reason>`。在会话中用 `/snapshot restore <id>` 恢复。
  - `SOUL.md`、`memories/`：quick 快照不包含它们。把文件复制为 `<file>.bak`，覆盖上一份副本。
  - 更新或大范围改动前：运行 `hermes backup`（完整 zip）。用 `hermes import <zip>` 恢复。
- **重启后生效。** tool 和 skill 的改动在新会话中生效（`/reset`）。配置改动需 `hermes gateway restart` 才对网关生效，CLI 和桌面应用需重新启动。
- **改动后验证。** 运行 `hermes config check` 和 `hermes doctor`；`hermes status` 显示当前生效状态；`hermes logs` 显示错误。
- **持续跟踪记录。** 更新或重装 Hermes，或修改其更新、凭据、`.env` 设置前，先阅读 `~/.hermes/TRACKING.md`。当上游问题阻碍某个本地选择时，在其中添加一条记录。
