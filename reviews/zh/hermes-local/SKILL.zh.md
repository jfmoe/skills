---
name: hermes-local
description: "本机部署了 Hermes Agent（Nous Research）。当任务涉及 Hermes——使用、配置、更新或排查它——或涉及 `~/.hermes/` 时使用。"
---

# Hermes Agent

Hermes Agent 以 git 方式安装在本机。本 skill 给出它的目录布局、查阅资料的位置和本地维护规则。Hermes 迭代很快：命令、参数、配置键和提供商以下列来源为准，不要凭记忆。

## 布局

- **Home：** `~/.hermes/`——`config.yaml`（设置）、`.env`（密钥）、`auth.json`、`state.db`、`logs/`、`skills/`、`SOUL.md`。设置了 `$HERMES_HOME` 时，由它替代 `~/.hermes`。
- **本地 git：** `~/.hermes/` 是一个没有远端的 git 仓库。它的白名单式 `.gitignore` 只跟踪 `config.yaml`、`SOUL.md`、`TRACKING.md` 和 `scripts/`。
- **源码：** `~/.hermes/hermes-agent/`，是 `NousResearch/hermes-agent` 的 git checkout。
- **入口：** CLI `~/.local/bin/hermes`（进入源码安装的启动脚本）、由 `hermes desktop` 从源码构建的桌面应用（`~/.hermes/hermes-agent/apps/desktop/release/mac-arm64/Hermes.app`），以及由 launchd 托管的消息网关（`ai.hermes.gateway`）。三者共用同一个 home，因此配置或凭据的改动会同时影响它们。

## 查阅位置

1. **内置 skill：** `~/.hermes/hermes-agent/skills/autonomous-ai-agents/hermes-agent/SKILL.md`。由上游维护，`hermes update` 会刷新它。先读它；它的路由表为每个主题指向一个参考文件。
2. **本地文档：** `~/.hermes/hermes-agent/website/docs/`，完整的文档站点。用 grep 检索。
3. **Web 索引：** `https://hermes-agent.nousresearch.com/docs/llms.txt`，每个已文档化的功能一行。本地文档无法回答时使用。
4. **CLI 帮助：** `hermes --help` 和 `hermes <command> --help` 给出已安装版本的命令和参数。运行命令前先查看。

## 维护规则

- **源码树只读。** 通过 CLI、`config.yaml`、`.env` 和 `~/.hermes/skills/` 修改 Hermes。用 `hermes skills` 安装和更新 skill。只用 `hermes update` 更新 Hermes。
- **自定义插件来自 `jfmoe/hermes-plugins`。** 在 `~/Coder/hermes-plugins/plugins/<name>/` 中修改插件，并遵循该仓库的 `AGENTS.md`；不要修改 `~/.hermes/plugins/` 中的安装副本。用 `hermes plugins install jfmoe/hermes-plugins/plugins/<name> --enable` 安装。推送改动后，运行 `hermes plugins update <name>`。`hermes update` 后，对每个自定义插件运行 `hermes plugins doctor <name>` 和插件测试。插件出问题时，先按其 README 的回退步骤恢复，再在仓库中修复插件。
- **每次更新前先审查。** 运行 `hermes update --check`。然后阅读一次提交标题：`git -C ~/.hermes/hermes-agent log --oneline HEAD..origin/main`，用 breaking、deprecat、remov、migrat、config、plugin、tts、voice、discord、approval 等词筛选。只有标题可能涉及本地个性化配置时，才打开完整提交。审查范围是提交标题；在这个仓库上逐文件 `git log -- <path>` 或审阅代码 diff 要花数分钟，收益很小。跟踪 `main` 渠道时，这些提交尚未进入发布版本，因此发布说明（`gh release list -R NousResearch/hermes-agent`）只适用于发布渠道。把相关改动逐项对照本地个性化配置：`config.yaml`、`.env`、`~/.hermes/TRACKING.md`、`SOUL.md`、自定义插件、skill、cron 任务和网关。`hermes update --plan` 显示哪些服务会重启。如果某项改动可能破坏个性化配置，先制定更新计划（受影响项、修复方式、回滚方式），得到用户批准后再执行。否则运行 `hermes backup` 和 `hermes update --yes`。更新完成后，在 `~/.hermes` 中提交配置迁移并验证，再向用户说明版本变化、主要改动、对每项个性化配置的影响，以及验证结果。
- **设置与密钥分开。** 用 `hermes config set KEY VAL` 修改设置；用 `hermes auth` 添加凭据。`.env` 只存放密钥。不要打印或提交密钥值。
- **只用自己的登录。** 保持 `auth.adopt_external_logins: false`。Hermes 只使用自己的登录（`hermes auth add <provider>`），因此永远不会刷新 Claude Code 或 Codex CLI 的登录。
- **先用 git 和内置工具备份。** 不要添加带日期的 `.bak` 文件。
  - git 跟踪的文件：每次改动前后各提交一次（`git -C ~/.hermes`）。从较早的提交恢复文件。Hermes 还会自动在 `backups/config/` 中保留 `config.yaml` 副本。
  - `.env`、`auth.json`、cron 及其他状态：运行 `hermes backup --quick --label <reason>`。在会话中用 `/snapshot restore <id>` 恢复。
  - `memories/`：quick 快照和 git 都不包含它。把文件复制为 `<file>.bak`，覆盖上一份副本。
  - 更新或大范围改动前：运行 `hermes backup`（完整 zip）。用 `hermes import <zip>` 恢复。
- **重启后生效。** tool 和 skill 的改动在新会话中生效（`/reset`）。配置改动需 `hermes gateway restart` 才对网关生效，CLI 和桌面应用需重新启动。
- **改动后验证。** 运行 `hermes config check` 和 `hermes doctor`；`hermes status` 显示当前生效状态；`hermes logs` 显示错误。
- **持续跟踪记录。** 更新或重装 Hermes，或修改其更新、凭据、`.env` 设置前，先阅读 `~/.hermes/TRACKING.md`。当上游问题阻碍某个本地选择时，在其中添加一条记录。
