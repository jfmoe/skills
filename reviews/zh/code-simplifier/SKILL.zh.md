---
name: code-simplifier
description: 在保留全部功能的前提下简化和改进代码，提高其清晰度、一致性与可维护性。除非另有指示，否则聚焦最近修改的代码。由一个 subagent 执行。
---

<!-- 基于 Anthropic 的 code-simplifier agent 修改。 -->

使用一个全新上下文的 `worker` subagent 执行简化。主 agent 负责范围和验收；worker 修改代码并验证。

如果你已经是被委派执行本次简化的 worker，读取 [references/simplifier.md](references/simplifier.md) 并直接执行，不要再次委派。

1. 确定目标：用户明确指定的范围，或当前任务的改动，包括相关的已暂存、未暂存和未跟踪文件。记录当前状态，保护用户的无关改动。
2. 使用 `spawn_agent`，设置 `agent_type="worker"` 和 `fork_turns="none"`。提供自包含的委托说明，包含仓库路径、精确的可写范围、排除项、目标改动、必须保持的行为、适用指令和已知检查。附上 `references/simplifier.md` 的绝对路径，并要求 worker 完整读取。授权范围内的修改与验证，禁止继续委派。如果无法使用 subagent，报告此限制，不由主 agent 执行简化。
3. 按会话的等待规则等待 worker 完成。只继续独立工作；不要修改 worker 的文件或重复它的探索。
4. 检查实际 diff 和验证证据。将具体缺口交回同一个 worker，在原范围内解决。报告验收的改动、检查和未解决的缺口。没有值得简化的内容也是有效结果。
