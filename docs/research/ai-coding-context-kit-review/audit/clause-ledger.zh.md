# 通用条款表

[English](clause-ledger.md) | 中文

| 主题 | 精确上游来源 | 通用落点 |
|---|---|---|
| 规划前先探索；保持只读；自行查明可发现事实；产出决策完备的计划 | `apps/cli/config/agent-presets/standard/agent.cordis.yml` 第 113–124 行 | `plan-code-changes`；用户级指令 |
| 优先少量证据充分的简化；要求当前消费方；区分生产、测试／文档和模糊用途；引入依赖时计算净删除量 | `.agents/skills/dsh-find-simplifications/SKILL.md` 第 8–31、47–80 行 | `audit-code-simplifications` |
| 每项设计都需要当前所有者和需求；公共选择需要证据；行为留在其所有者处 | `packages/AGENTS.md` 第 10–12 行 | 用户级和项目级指令；简化及 review Skill |
| 核实准确 base/head 并阅读周边代码；优先正确性、生命周期、安全和必需行为 | `.agents/skills/dsh-code-review/SKILL.md` 第 8–18 行 | `review-code-changes` |
| 审查接口两端；追踪生命周期、消费方、执行点、派生状态、完整边界、真实入口、测试强度和 transcript 变化 | `.agents/skills/dsh-code-review/SKILL.md` 第 20–49 行 | `review-code-changes` |
| 从技术上核实每条 review 意见；在引入问题的层修复；委派报告不是完成证明 | `.agents/skills/dsh-code-review/SKILL.md` 第 49 行；`docs/cookbook/responding-to-pr-review-on-a-stack.md` 第 9–24 行 | Review Skill 和项目级指令 |
| 运行能在回归出现时失败的最小证据；CI 负责穷尽覆盖和平台矩阵 | `AGENTS.md` 第 87–93 行；`.agents/skills/dsh-pre-push-checks/SKILL.md` 第 27–64 行 | `select-relevant-checks`；用户级和项目级指令 |
| 覆盖率只证明代码执行过，不证明发布行为正确；未覆盖代码可能是死代码 | `docs/testing.md` 第 9–13 行 | 测试子目录指令；检查选择 Skill |
| 测试描述行为，而不是确立正确性；过时行为应与其测试同步修改 | 根目录 `AGENTS.md` 第 122 行 | 项目级和测试子目录指令；简化、review 和检查选择 Skill |
| 信任同进程类型接口；敌意输入验证和测试应放在真实的不可信边界 | 根目录 `AGENTS.md` 第 116 行 | 项目级和测试子目录指令；简化、review 和检查选择 Skill |
| 只 mock 昂贵或不确定的边界；检查外部状态；测试真实入口 | `docs/testing.md` 第 21–35 行；`examples/AGENTS.md` 第 7–14 行 | 测试子目录指令；review 和检查选择 Skill |
| 门禁必须能在目标回归存在时失败 | `docs/testing.md` 第 34 行；`docs/cookbook/responding-to-pr-review-on-a-stack.md` 第 22 行 | 测试子目录指令；review Skill |
| 测试资源即使遇到失败、重试和超时也由测试自行清理 | `docs/testing.md` 第 27–29 行 | 测试子目录指令 |
| 每项事实只有一个真源；文档描述当前状态；先修改所有者再生成派生产物 | `docs/AGENTS.md` 第 7–17、34–45、59–75 行 | `apply-documentation-standards`；文档子目录 |
| 文档格式、字数预算、物理换行和双语结构 | `docs/AGENTS.md` 第 36–57 行；`docs/i18n/*` | 根据用户明确要求，从通用文档 Skill 中排除；仅用于生成本审阅包的中文对侧文件。 |
| 保留每个命题：主体、条件、时机、语气强度、例外、所有权、副作用、失败和后果 | `.agents/skills/dsh-prose-standard/SKILL.md` 第 28–42 行 | `review-code-prose` |
| 所需文字取决于所在位置；提示词和可见字符串属于行为 | `.agents/skills/dsh-prose-standard/SKILL.md` 第 44–61 行 | Prose Skill；Agent 产品子目录 |
| CoT 泄漏的一条判断、八类分类体系、明确保留规则及先改所有者的工作流 | `.agents/skills/dsh-trim-cot-leakage/SKILL.md` 第 8–45 行，以及两个 reference | 独立的 `trim-cot-leakage` Skill |
| 面向模型的约定只使用任务相关概念；稳定文本逐字固定；动态行为使用快照／e2e 覆盖 | `packages/AGENTS.md` 第 13 行；`AGENTS.md` 第 108、124–127 行 | Agent 产品子目录；review 和测试 Skill |
| 在作出决定的操作中执行规则；只在提交点之后发布状态；对完整结果施加边界 | `packages/AGENTS.md` 第 14–16 行 | 项目级和 Agent 产品指令；review Skill |
| 执行机制不可用时默认拒绝；只有明确批准才授权操作 | `native/landlock-run/AGENTS.md` 第 9–16 行；`docs/subsystems/approval.md` 第 21–33、84–88 行 | 安全子目录 |
| 从子进程环境移除秘密；使用私有、随机、独占的临时路径；对 link 形态路径执行 unlink | `docs/defensive-patterns.md` 第 27–33 行 | 安全子目录 |
| 异步状态不等同于同步状态；dispose 必须等待完全停稳；回调异常应被隔离 | `docs/defensive-patterns.md` 第 7–25 行 | 异步子目录 |
| 实验状态不会降低工程、安全、文档、生命周期、测试、不变量或快照要求 | `packages/experimental/AGENTS.md` 第 5–9 行 | 项目级指令 |
| 钩子保持精简；贡献者只运行一次相关检查；CI 负责穷尽门禁 | `docs/development.md` 第 109–123 行 | 候选 hook／CI 分工 |
| 更新 review 指南需要来源反馈、已落地证据、独立分类和人工判断，不能从单次事故过度泛化 | `docs/cookbook/maintaining-dsh-code-review.md` 第 9–17、19–48 行 | Review Skill 来源记录和项目级维护说明 |
