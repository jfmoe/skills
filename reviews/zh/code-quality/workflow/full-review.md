# 完整审查：代码质量

重型、系统性的审查。**仅由用户触发**，绝不自行进入此模式。比快速审查更慢、更彻底，带分阶段阅读和自我验证。

## 触发条件

仅当用户明确要求“完整审查”“架构审查”“设计审查”或“重构评估”时。

## 步骤

### 1. 上下文摄入

在广泛阅读之前，先写下：

- 审查目标：实际被评判的是什么（一个模块、一个子系统、一个重构计划、一份配置）。
- 必读：对目标至关重要的代码、配置或测试。
- 可选上下文：可能解释某个决策的邻近代码。
- 待定问题：哪些不确定、可能需要用户确认。

### 2. 分阶段阅读

按问题域加载参考文档，而不是一次全部加载。阅读最近的 `AGENTS.md` 或 `CLAUDE.md`。只有当具体信号指向某份原则、模式、重构或范式文档时才拉取它。分阶段读代码。从目标开始，只有当某个发现需要时才扩大范围。

### 3. 系统矩阵

逐一检查以下维度，为每条发现记录证据：

- 变更方向与成本：接下来最可能发生什么变化，当前结构让它变得多昂贵。
- 原则张力：DRY vs KISS、抽象 vs 重复、灵活性 vs YAGNI。指出权衡，不要教条地选边。
- 模式正当性：对每个被指名的模式，确认它所管理的变化点确实存在。
- 坏味道识别：过长函数、重复知识、基本类型偏执、特性依恋、霰弹枪式修改、发散式变化、薄包装。
- 范式适配：命令式/面向对象/函数式核心/面向数据/状态机是否与问题匹配，还是与之对抗。
- 测试覆盖：行为是否被足够好地固定，可以安全重构。

### 4. 自我验证高严重度发现

对每条高严重度发现，重新核对证据，说明你的置信度，并主动考虑误报的可能：这个结构会不会是有意为之，或者由一个你尚未看到的变化原因所驱动？无法通过这一关的发现要降级或丢弃。

### 5. 确认停顿

在建议或执行任何以下操作之前停下来询问：跨文件重构、架构迁移或批量修改。摆出计划及其成本；由用户决定。

## 输出格式

```text
Findings

- [severity, confidence] path:line Title
  Fact: observable evidence.
  Impact: change cost, readability, correctness, testability.
  Judgment: principle, pattern, smell, or paradigm mismatch.
  Evidence: support, counter-evidence, and remaining uncertainty.
  Recommendation: smallest sufficient change.
  Verification: command/check, or why none is needed.

Open Questions
- Items needing user or project confirmation.

Notes
- Downgraded, deliberate, or tool-handled items, with why.
```

按类别对发现分组。明确说明你降级了什么以及为什么。

## 停止规则

- 未经明确要求不要修改代码。
- 跨文件重构、迁移和批量修改必须经过确认停顿。
- 不要为了满足某条原则而强行制造发现，也不要仅凭相似性就做抽象。
- 在每条发现中区分事实、判断和建议。
