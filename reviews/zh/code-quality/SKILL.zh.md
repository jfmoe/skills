---
name: code-quality
description: 用于评估或改进代码质量，包括可维护性、抽象、设计原则与模式、重构、代码坏味道、测试设计和架构。也可通过在完整审查上叠加压力模式来处理明确的“热核级”或“极其严格的结构性审查”请求。
---

# 代码质量

使用本 Skill 判断代码、测试、架构、重构计划和抽象是否具有合理的结构、变更边界和维护成本。

## 进入条件

当涉及可维护性、设计质量、测试质量或测试坏味道、抽象边界、重构、代码坏味道、编程范式选择、设计模式使用或设计原则时，激活本 Skill。按信号加载参考叶子文档，而不是一次全部加载。

如果任务没有明确要求代码质量分析，即使本 `SKILL.md` 已被加载，也不要加载 `references/` 下的任何文档。

## 模式选择

共有三种模式。默认使用快速审查。

| 模式 | 触发条件 | 阅读 |
|-|-|-|
| 快速审查 | 日常自检、小型 diff、PR 审查的默认模式 | `./workflow/fast-review.md` |
| 完整审查 | 用户明确说“完整审查”“架构审查”“系统性审查”“重构评估” | `./workflow/full-review.md` |
| 分析 | 用户要求讨论、头脑风暴、设计探索、范式比较、机制分析 | `./workflow/analysis.md` |
| 热核压力 | 用户明确说“热核”“thermonuclear”“thermo-nuclear”或“极其严格的结构性审查” | 先运行完整审查，然后阅读 `./workflow/thermo-pressure.md` |

热核压力是叠加在完整审查之上的模式，而不是第四种模式：目标对象先经过完整审查的上下文摄入、系统矩阵、自我验证和确认停顿，然后再进入压力环节。快速审查和分析模式从不与它组合。

## 判断顺序

1. 确定主要关切：正确性、可读性、变更成本、可测试性、性能还是交付成本。
2. 判断问题属于原则、模式、重构还是范式范畴。
3. 路由到下方相关的叶子文档。
4. 只报告证据充分的问题。

| 信号 | 首先阅读 | 常搭配 |
|-|-|-|
| DRY、重复知识、错误的抽象 | [DRY](./references/design-principles/dry.md) | 三次法则、重复代码 |
| 两个相似案例、过早抽象 | [三次法则](./references/design-principles/rule-of-three.md) | DRY、KISS |
| 不必要的复杂性 | [KISS](./references/design-principles/kiss.md) | YAGNI、深模块 |
| 过早的扩展点、不需要的灵活性 | [YAGNI](./references/design-principles/yagni.md) | KISS、深模块 |
| SOLID、职责、可替换性、接口大小、依赖方向 | [SOLID](./references/design-principles/solid.md) | 组合优于继承、依赖倒置 |
| 职责分配、行为应归属何处 | [GRASP](./references/design-principles/grasp.md) | Tell Don't Ask、特性依恋 |
| 消息链、对远处对象结构的了解 | [得墨忒耳法则](./references/design-principles/law-of-demeter.md) | 深模块、外观 |
| 调用方先查询字段再做领域决策 | [Tell Don't Ask](./references/design-principles/tell-dont-ask.md) | GRASP、特性依恋 |
| 继承与组合、mixin、子类化 | [组合优于继承](./references/design-principles/composition-over-inheritance.md) | SOLID、依赖倒置 |
| 依赖倒置、DI、组合根 | [依赖倒置](./references/design-principles/dependency-inversion.md) | 适配器、仓库、工作单元 |
| TDD、红-绿-重构、行为优先的测试 | [TDD](./references/design-principles/tdd.md) | 安全重构 |
| 测试设计、测试坏味道、脆弱/不稳定的测试、过度 mock、覆盖率策略、更少更强的测试 | [测试原则](./references/testing/principles.md) | 测试坏味道、TDD |
| 重构时测试被破坏、变更侦测器、晦涩/重复的测试、测试配置/工具 | [测试坏味道](./references/testing/test-smells.md) | 测试原则、代码坏味道 |
| 领域驱动设计、限界上下文、领域建模 | [DDD](./references/design-principles/ddd.md) | 深模块、仓库 |
| 抽象深度、信息隐藏、浅模块 | [深模块](./references/design-principles/deep-modules.md) | KISS、外观 |
| 对象创建随类型/配置/环境变化 | [工厂](./references/design-patterns/factory.md) | 抽象工厂、建造者 |
| 配套的产品族一起变化 | [抽象工厂](./references/design-patterns/abstract-factory.md) | 工厂、建造者 |
| 复杂的分阶段构造 | [建造者](./references/design-patterns/builder.md) | 工厂、抽象工厂 |
| 在稳定调用点背后变化的算法/行为 | [策略](./references/design-patterns/strategy.md) | 工厂、函数式核心 |
| 一个事件通知多个订阅者 | [观察者](./references/design-patterns/observer.md) | 事件驱动、命令 |
| 外来接口需要翻译 | [适配器](./references/design-patterns/adapter.md) | 外观、依赖倒置 |
| 横切行为包裹调用/对象 | [装饰器](./references/design-patterns/decorator.md) | 外观、薄包装函数 |
| 复杂子系统之上的简单界面 | [外观](./references/design-patterns/facade.md) | 深模块、适配器 |
| 请求需要排队、重试、审计、撤销、调度 | [命令](./references/design-patterns/command.md) | 状态、观察者 |
| 随状态变化的行为、GoF 状态模式 | [状态](./references/design-patterns/state.md) | 状态机、命令 |
| 在稳定节点类型（AST/树/schema）上变化的操作 | [访问者](./references/design-patterns/visitor.md) | 策略 |
| 持久化边界、ORM 隔离 | [仓库](./references/design-patterns/repository.md) | 工作单元、依赖倒置 |
| 跨仓库的事务/一致性 | [工作单元](./references/design-patterns/unit-of-work.md) | 仓库、依赖倒置 |
| 作为保持行为的 Fowler 式工作的重构 | [Fowler 重构](./references/refactoring/fowler-refactoring.md) | 安全重构、代码坏味道 |
| 通用的坏味道分诊与坏味道地图 | [代码坏味道](./references/refactoring/code-smells.md) | 具体的重构叶子文档 |
| 安全的保持行为的重构流程 | [安全重构](./references/refactoring/safe-refactoring.md) | Fowler 重构、TDD |
| 函数混合多个阶段、策略、I/O、分支 | [过长函数](./references/refactoring/long-function.md) | 提取函数、重复代码 |
| 重复的规则、映射、schema、被复制的知识 | [重复代码](./references/refactoring/duplicated-code.md) | DRY、提取函数 |
| 字符串/字典/基本类型承载稳定的领域含义 | [基本类型偏执](./references/refactoring/primitive-obsession.md) | DDD、面向数据 |
| 函数嫉妒另一个对象/模块的数据 | [特性依恋](./references/refactoring/feature-envy.md) | 移动函数、GRASP |
| 一次变更需要许多处分散的编辑 | [霰弹枪式修改](./references/refactoring/shotgun-surgery.md) | 发散式变化、移动函数 |
| 一个模块因许多不相关的原因而变化 | [发散式变化](./references/refactoring/divergent-change.md) | 霰弹枪式修改 |
| 帮助函数/包装不增加任何语义边界 | [薄包装函数](./references/refactoring/thin-wrapper-function.md) | KISS、外观 |
| 把连贯的一个阶段提取为函数 | [提取函数](./references/refactoring/extract-function.md) | 过长函数、内联函数 |
| 内联一个有误导性或过浅的函数 | [内联函数](./references/refactoring/inline-function.md) | 提取函数 |
| 把行为移动到更合适的归属处 | [移动函数](./references/refactoring/move-function.md) | 特性依恋、GRASP |
| 直接的步骤、脚本、处理器、编排 | [命令式](./references/programming-paradigms/imperative.md) | 声明式 |
| 配置、schema、表驱动、声明 | [声明式](./references/programming-paradigms/declarative.md) | 命令式 |
| 对象标识、状态、不变量、多态 | [面向对象](./references/programming-paradigms/object-oriented.md) | 组合优于继承、SOLID |
| 将纯逻辑与副作用外壳分离 | [函数式核心](./references/programming-paradigms/functional-core.md) | 策略、声明式 |
| 显式的数据形状、映射、schema、表 | [面向数据](./references/programming-paradigms/data-oriented.md) | 基本类型偏执、声明式 |
| 事件、钩子、事件总线、发布/订阅、领域事件 | [事件驱动](./references/programming-paradigms/event-driven.md) | 观察者、命令 |
| 状态/状态值/事件/迁移的工作流 | [状态机](./references/programming-paradigms/state-machine.md) | 状态、资源生命周期 |
| 资源获取、所有权、清理 | [资源生命周期](./references/programming-paradigms/resource-lifecycle.md) | 状态机、工作单元 |
| 异步任务、取消、超时、背压 | [异步/并发](./references/programming-paradigms/async-concurrency.md) | 事件驱动、资源生命周期 |

当术语不清晰或不一致时，阅读[术语表](./glossary.md)。

## 输出契约

以发现开头。原则不是机械的规则；要解释其中的权衡。模式不是默认模板；先证明变化点确实存在。将事实、推断、判断和建议分开。不要重复格式化工具或 linter 能机械发现的问题。

输出格式因模式而异。遵循对应的工作流文档（`./workflow/fast-review.md`、`./workflow/full-review.md` 或 `./workflow/analysis.md`）。分析模式给出的是权衡和选项，而不是发现清单。

输出语言遵循全局、项目或用户指令的要求；未指定时使用当前对话的语言。

## 停止规则

- 不要为了满足某条原则而强行制造发现。
- 不要仅仅因为代码看起来相似就做抽象。
- 不要在未证明共享意图的情况下把相似代码当作重复知识。
- 不要自动应用重构、补丁、不安全的修复或批量抑制。
- 在只读或分析任务中不要写入文件修改。
- 不要报告格式化工具或 linter 能机械发现的问题。如相关，提一次即可，然后继续。
