# 用户级指令来源

[English](SOURCES.md) | 中文

除非另有说明，所有上游路径和行号均指向 `deepseek-ai/deepseek-harness` 提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`。

| 候选条款 | 精确来源 | 处理方式 |
|---|---|---|
| 先探索；自行查明可发现事实；只就用户拥有的选择提问 | `apps/cli/config/agent-presets/standard/agent.cordis.yml` 第 116、120–124 行 | 保留原意，删除产品专用工具名。 |
| 公共选择需要当前所有者、需求、消费方和证据 | `packages/AGENTS.md` 第 10–12 行 | 保留并通用化。 |
| 优先现有模式，避免推测性扩张 | `apps/cli/config/agent-presets/standard/agent.cordis.yml` 第 116 行；`.agents/skills/dsh-code-review/SKILL.md` 第 33–35 行 | 保留并通用化。 |
| 只运行一次最小可信证据 | 根目录 `AGENTS.md` 第 87–93 行；`.agents/skills/dsh-pre-push-checks/SKILL.md` 第 27–37、62–64 行 | 删除 DeepSeek 命令和 push 流程后保留。 |
| 从技术上核实 review 主张 | `.agents/skills/dsh-code-review/SKILL.md` 第 49 行；`docs/cookbook/responding-to-pr-review-on-a-stack.md` 第 17–24 行 | 保留并通用化。 |
| 报告范围、假设、改动、检查和缺口 | `.agents/skills/dsh-prose-standard/SKILL.md` 第 65–71 行；`.agents/skills/dsh-pre-push-checks/SKILL.md` 第 83–92 行 | 改写。 |

中文文件只翻译候选条款，不新增政策。
