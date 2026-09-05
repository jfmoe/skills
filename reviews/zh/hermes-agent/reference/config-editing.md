# 配置编辑与提供商/模型工作流

安全修改 Hermes 配置的稳定机制，加上切换提供商/模型的有序工作流，确保改动真正生效。具体的键、配置段和提供商名称**不会**在这里列出——它们会过期。现场发现它们（见下方指引）。

> 运行任何命令之前，用 `hermes <cmd> --help` 确认其标志（SKILL.md 规则 2）。如果这里没有覆盖你的情况，获取文档索引（规则 1）。

## 安全的配置编辑规范（采纳自 Hermes 捆绑的 autonomous-ai-agents skill）

来源：捆绑 skill（见 SKILL.md 机器事实）和本地文档页 `~/.hermes/hermes-agent/website/docs/user-guide/skills/bundled/autonomous-ai-agents/`。

- **使用专用命令，不要盲目编辑 YAML。** `hermes config edit` 在 `$EDITOR` 中打开文件；`hermes config set KEY VAL` 设置单个值（点号键，例如 `section.key`）。这些能保持文件有效，避免破坏结构。
- **设置与密钥是分开存储的。** 非密钥设置在 `config.yaml`；API 密钥和令牌在 `.env`。用 `hermes config path` 和 `hermes config env-path` 查找路径。
- **API 密钥走 `hermes auth`**（凭据管理器/池），不要手工编辑 `.env`。不要以明文打印密钥，绝不提交到任何仓库。
- **编辑后验证：** `hermes config check`（缺失/过期的配置）和 `hermes config migrate`（拉入新选项 / 迁移弃用的设置）。淘汰特定的弃用模型是一个独立的、更窄的命令——`hermes migrate`（目前是 `hermes migrate xai`）；运行 `hermes migrate --help` 查看它当前覆盖什么。
- **`security.redact_secrets` 默认开启**，并在启动时快照。会话中途切换它（甚至通过工具调用设置环境变量）不会影响正在运行的进程——从终端修改它，然后开一个新会话。这是有意设计，防止 agent 对自己关闭脱敏。
- **`approvals.mode`：** `manual`（默认；破坏性 shell 命令前提示）/ `smart`（辅助 LLM 自动批准低风险操作）/ `off`（跳过所有提示，同 `--yolo`）。单次调用绕过：`hermes --yolo …`。YOLO/`off` 不会禁用密钥脱敏。
- **重启后生效。** 配置编辑只在新进程中生效：退出并重新启动 CLI，或 `/restart` gateway。（工具/skill/源码改动的完整重启映射：`reference/troubleshooting.md`。）

> **配置段、键、默认值和当前值的清单没有复制到这里**——那是最容易过期的东西。查看存在什么、设置了什么：直接读 `~/.hermes/config.yaml`，或运行 `hermes config show`。完整带注释的参考，读本地文档 `~/.hermes/hermes-agent/website/docs/user-guide/configuration.md`（网络镜像：`https://hermes-agent.nousresearch.com/docs/user-guide/configuration`）。

## 提供商 / 模型工作流（有序——这是稳定的部分）

排序的意义：模型/提供商切换只有在凭据先存在、进程后重启的情况下才真正"生效"。按顺序执行。

1. **先配置提供商的凭据。** `hermes auth`（交互式）或 `hermes auth add <provider>`。如果在凭据设置好之前就在模型选择器里选了提供商，它只会在运行时失败。用 `hermes auth list` / `hermes auth status` 验证。
2. **选择默认模型 / 提供商。** `hermes model`（交互式选择器；`--refresh` 重新获取每个提供商的实时模型列表）。持久化的提供商在 `config.yaml` 的 `model.provider` 下。
3. **配置回退**（主模型失败时尝试——限流、过载、连接错误）。`hermes fallback --help` 查看 `add` / `list` / `remove` / `clear`。
4. **重启使其生效。** 退出并重新启动 CLI，或 `/restart` gateway。
5. **验证实际生效的内容。** `hermes status`（加 `--all` 查看脱敏后的完整视图）和 `hermes model` 确认当前生效的提供商/模型——不要假设编辑已经生效。

> **提供商列表及它们的环境变量 / 认证方式没有复制到这里**（它们经常变化）。查看可用项及各自的认证方式：运行 `hermes model`，或读本地文档 `~/.hermes/hermes-agent/website/docs/integrations/providers.md`（网络镜像：`https://hermes-agent.nousresearch.com/docs/integrations/providers`）。一次性覆盖而不改配置：`hermes -m <model> --provider <provider> …`（见 `hermes chat --help`）。
