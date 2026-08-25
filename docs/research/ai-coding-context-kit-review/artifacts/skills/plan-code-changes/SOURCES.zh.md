# 来源和通用化改动

[English](SOURCES.md) | 中文

## 精确上游来源

- 主要来源：提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` 中 `apps/cli/config/agent-presets/standard/agent.cordis.yml` 第 113–124 行。
- 已审阅的重复提示词：`code/agent.cordis.yml` 第 120–131 行和 `cordis/agent.cordis.yml` 第 101–112 行。
- 补充所有权和证据规则：根目录 `AGENTS.md` 第 87–93 行及 `packages/AGENTS.md` 第 10–16 行。

## 保留的原文写法

“Explore first”“Resolve discoverable facts”和“Make the plan decision-complete”三段保留上游写法，只删除产品专用工具名和展示机制。

## 通用化改动

- 删除 `exit_plan_mode`、`todo_write`、请求缓存和固定工具目录机制，因为它们依赖 DeepSeek 运行时。
- 将运行时专用退出协议替换为通用完成条件：“返回完整计划并保持只读”。
- 仅使用上游 review、包和测试指令已有的条款扩充计划字段。
- 新增简体中文翻译，不增加工作流规则。

原文快照：`../../../upstream/repository/apps/cli/config/agent-presets/standard/agent.cordis.yml`。
