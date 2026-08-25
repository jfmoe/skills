# 来源处置表

[English](disposition-ledger.md) | 中文

本表解释各类来源的处置方式；逐文件决定仍以 `source-manifest.tsv` 为准。

## AGENTS 指令

| 来源 | 处置 |
|---|---|
| 根目录 `AGENTS.md`、`docs/AGENTS.md`、`packages/AGENTS.md`、`examples/AGENTS.md` | 提取通用的规划、所有权、文档、面向模型和测试规则；删除仓库布局、具体命令、包名、格式和双语政策。 |
| `.agents/notes/{,implemented,archived}/AGENTS.md` | 提取当前真源、决策记录和冻结历史规则；不把 DeepSeek 的三文件生命周期当成通用默认值。 |
| 根目录、`examples/`、`packages/`、`.agents/notes/implemented/` 和 `vendor/` 中的 `CLAUDE.md` | 将每个符号链接 blob 作为生效入口证据保留。它们都解析到同目录的 `AGENTS.md`，因此不新增通用条款，但应明确分类，不能静默遗漏。 |
| `native/landlock-run/AGENTS.md`、`packages/web/AGENTS.md` | 将默认拒绝式执行、路径安全和携带凭据请求禁止跟随重定向等规则放入安全子目录指令。 |
| `packages/experimental/AGENTS.md` | 提取“实验状态不会降低工程、安全、文档、生命周期或测试要求”这一规则。 |
| `vendor/AGENTS.md`、`website/AGENTS.md` | 将受保护源代码和规范源／生成投影规则放入项目指令及机械门禁。 |
| `.github/AGENTS.md`、`packages/client/AGENTS.md`、`packages/schedule/AGENTS.md`、`scripts/AGENTS.md` | 保留为已审阅的项目专属参考；其中通用的测试和生命周期命题已从相应真源提取。 |
| 4 个快照 `AGENTS.md` | 作为测试数据排除，但保留逐字节镜像和明确的 manifest 行。 |

## Skill

| 上游 Skill | 处置 |
|---|---|
| `.claude/skills` | 保留这个指向 `.agents/skills` 的 Claude 发现入口 symlink blob；它暴露相同的 11 个仓库 Skill，不构成第 12 个 Skill。 |
| `dsh-code-review` | 独立 fork 为 `review-code-changes`。 |
| `dsh-doc-standards` | 独立 fork 为 `apply-documentation-standards`；根据用户要求删除格式、字数预算和双语布局规则。 |
| `dsh-find-simplifications` | 独立 fork 为 `audit-code-simplifications`。 |
| `dsh-pre-push-checks` | 独立 fork 为 `select-relevant-checks`；排除 push 和堆叠分支改写流程。 |
| `dsh-prose-standard` | 独立 fork 为 `review-code-prose`，并保留其示例。 |
| `dsh-trim-cot-leakage` | 独立 fork 为 `trim-cot-leakage`，完整保留分类体系、例外、工作流、示例和召回检索式；不得并入 prose Skill。 |
| `dsh-archive-agent-notes` | 仅作参考。其“未来决策价值”判断用于决策记录指南，但具体生命周期和封存三文件属于项目政策。 |
| `dsh-doc-site-sync` | 将规范源／投影机制提取到项目门禁；VitePress 和双语路由仍属项目专有。 |
| `dsh-merging-stacked-prs` | 不进入通用默认值，因为它会改变远程堆叠状态，并依赖仓库政策及 GitHub stack 能力。 |
| `dsh-translate-docs` | 作为本双语审阅包的翻译参考，不生成通用候选 Skill。 |
| `record-browser-gif` | 排除强制 GIF 和 assets 分支流程；将实际 UI 路径验证保留为测试原则。 |
| 2 个 Cordis preset 内置 Skill | 作为产品运行时创作流程排除；“写代码前检查真实接口”这一通用原则保留在项目指南中。 |

## Preset 和补充政策

标准 preset 的计划模式文本 fork 为 `plan-code-changes`；code 与 Cordis preset 中的重复文本登记为参考。极简 Shell 指导和 Cordis 自修改 persona 仍属于产品运行时。测试、防御模式、开发钩子、review 维护、review 响应、审批、Agent Note 和翻译政策贡献的精确条款列在 `clause-ledger.zh.md` 中。
