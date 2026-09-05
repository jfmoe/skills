# 故障排查与恢复

稳定的诊断和回滚**流程**。症状清单会过期，因此不复制到这里——当某个症状未被覆盖时，获取文档索引（SKILL.md 规则 1）。运行前用 `hermes <cmd> --help` 确认标志（规则 2）。

## 诊断三板斧（从这里开始，按顺序）

1. `hermes doctor` — 检查配置和依赖。`hermes doctor --fix` 尝试自动修复。它还会显示安全公告（用 `hermes doctor --ack <id>` 确认）。
2. `hermes status` — 组件状态；`hermes status --all` 查看脱敏后的完整视图，`--deep` 做更慢但更彻底的检查。
3. 日志 — `hermes logs`（默认 `agent.log`，最后 50 行）。常用标志：`-f`（持续跟踪）、`--level ERROR`、`--component gateway|agent|cron`、`--since 1h`，`hermes logs list` 查看可用文件。文件位于 `~/.hermes/logs/` 下。

## 常见故障形态（流程，而非症状目录）

- **模型 / 提供商不工作：** 先 `hermes doctor` → 用 `hermes auth`（或 `hermes auth add <provider>`）重新认证提供商 → 确认密钥/凭据存在。完整的提供商工作流见 `reference/config-editing.md`。
- **改动没有生效：** 这几乎总是重启问题，而不是编辑本身坏了。
  - 工具 / skill 改动 → `/reset`（新会话）；它们不会在会话中途生效。
  - 配置改动 → `/restart` gateway，或退出并重新启动 CLI。
  - 源码改动 → 完全重启进程。
- **更新破坏了安装 / 回滚：** 用 `hermes import <zipfile>` 恢复备份 zip（`--force` 覆盖）。备份是 zip 文件，不在固定目录——`hermes backup` 会生成一个（默认 `~/hermes-backup-<timestamp>.zip`；`--quick` 只备份关键状态），`hermes update` 也可以做更新前备份。用 `ls ~/hermes-backup-*.zip` 定位候选文件，通过 `hermes backup --help` / `hermes update --help` 确认路径。`~/.hermes/hermes-agent.broken-<timestamp>` 目录是失败/有风险的 `hermes update` 搁置的旧源码——残留物，不在使用。文件系统检查点（`/rollback` 历史）通过 `hermes checkpoints` 管理（`status` / `prune` / `clear`）。
- **更新后模型或设置被弃用/淘汰：** 一般配置用 `hermes config migrate`；特定被弃用模型用 `hermes migrate`（`hermes migrate --help`）。
- **其他 / 更深入：** 查阅本地文档（规则 1）——从 `~/.hermes/hermes-agent/website/docs/reference/faq.md` 开始，或 `grep -ril <症状> ~/.hermes/hermes-agent/website/docs/`。本地捆绑 skill `~/.hermes/skills/autonomous-ai-agents/hermes-agent/SKILL.md` 有更长（过期更快）的故障排查章节，值得浏览以了解 gateway/平台特定的案例。

## 恢复顺序（更新或编辑把它弄坏之后）

1. **先诊断再改动** — `hermes doctor` 和 `hermes status` 看清到底哪里出了问题；检查 `hermes logs --level ERROR`。
2. **快照当前状态** — 开始回退之前先 `hermes backup --quick`，这样失败的恢复本身也是可逆的。
3. **恢复最近的好备份** — `hermes import <zipfile>`（按上面的回滚说明定位 zip）。
4. **重新验证** — `hermes config check`，然后再跑一次 `hermes doctor`；重新启动并用 `hermes status` 确认。
