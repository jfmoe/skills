# AI 编程上下文套件——审阅包

[English](README.md) | 中文

本目录是一份从零重建、未启用的审阅包，来源固定为 `deepseek-ai/deepseek-harness` 的提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`。

本审阅包以证据为先。机器可读的 manifest 覆盖 70 个原文镜像文件：20 个 `AGENTS.md`、5 个生效的 `CLAUDE.md` 符号链接（分别指向同目录的 `AGENTS.md`）、1 个把相同 11 个仓库 Skill 暴露给 Claude 的 `.claude/skills` 符号链接、这 11 个 Skill 目录及其配套文件、4 个已发布的 Agent preset、2 个 preset 内置 Skill、它们直接引用的开发和翻译规则，以及 MIT 许可证。范围更广的提示词扫描共记录 125 条路径，其中包括已识别的 Agent 指令和 Skill 发现入口、产品运行时提示词、fixture、快照和历史 Agent Note；这些内容均作为候选范围接受检查，但不进入通用 AI 编程上下文。

本目录中的任何内容都没有安装或生效。候选入口使用 `SKILL.md.review` 和 `AGENTS.md.review`，UI 元数据使用 `openai.yaml.review`。原文镜像将可能触发发现机制的文件名改为 `.orig`，文件内容保持逐字节一致。

## 目录结构

- `audit/`：来源 manifest、提示词范围扫描、处置表、条款表、校验器和验证报告。
- `upstream/`：从固定提交复制的逐字节一致证据。
- `artifacts/user/`：候选用户级长期指令。
- `artifacts/project/`：候选项目级和子目录指令、钩子、CI 工作流、配置及校验器。
- `artifacts/skills/`：7 个相互独立的候选 Skill。
- `artifacts/registry/upstream/`：供后续推广使用的 fork 原文快照和元数据。

## 翻译约定

每份派生产物都有简体中文对侧文件。Markdown 提示词产物使用同目录的 `.zh.md` 形式；可执行文件或结构化文件只保留一份规范实现，同时提供同目录的中文 `.zh.md` 说明，避免两套可执行逻辑发生漂移。每个产物单元还包含中英文来源记录，列明精确的上游文件和行号范围。

`upstream/` 中逐字节一致的镜像属于证据，不是派生产物，因此有意不翻译；修改其文本会破坏哈希证明。该目录的双语 README 会说明这一边界。

## 候选 Skill

| Skill | 用途 |
|---|---|
| `plan-code-changes` | 以只读方式探索仓库并编写决策完备的实现计划。 |
| `audit-code-simplifications` | 根据证据删除、折叠、降级现有设计或改用依赖。 |
| `review-code-changes` | 对分支、PR、提交范围或工作区差异进行语义 review。 |
| `select-relevant-checks` | 根据改动面选择最小但可信的测试和检查。 |
| `apply-documentation-standards` | 按语义和所有权放置及审查文档，不附加格式政策。 |
| `review-code-prose` | 保留完整约定，同时删减重复、过程叙述和修饰。 |
| `trim-cot-leakage` | 独立识别并修复推理过程泄漏，完整保留分类体系、示例和召回检索式。 |

独立的上游 Skill 在候选产物中仍然保持独立。特别是，`dsh-trim-cot-leakage` 不并入 `review-code-prose`；两个 Skill 只相互引用。

## 建议审阅顺序

1. 阅读 `audit/source-manifest.zh.md` 和 `audit/prompt-surface-scan.tsv`。
2. 审阅 `audit/disposition-ledger.zh.md` 和 `audit/clause-ledger.zh.md`。
3. 将每份产物与其 `SOURCES.zh.md` 及固定版本原文镜像进行对照。
4. 将英文和中文对侧文件一起审阅。
5. 运行 `node audit/scripts/verify-review-bundle.mjs`；本地存在上游克隆时，再传入 `--upstream <clone>`，从固定 Git tree 重新推导完整发现集合。
6. 批准推广前阅读 `audit/validation-report.zh.md`。

推广、安装、重新生成 registry，以及将候选指令复制到真实用户或项目上下文，都需要另一次明确授权。
