# 验证报告

[English](validation-report.md) | 中文

已于 2026-08-22 根据 `deepseek-ai/deepseek-harness` 提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` 完成验证。所有必需检查均通过。

## 检查结果

| 检查面 | 结果和证据 |
|---|---|
| 固定上游语料 | `source-manifest.tsv` 的 70 行均与固定 Git tree 中的路径、blob SHA、行数和字节一致。校验器的离线模式和 `--upstream <clone>` 模式均通过；后者会重新推导 tree 对照，不信任 manifest 自述。 |
| 发现完整性 | 固定 tree 包含 11 个仓库 Skill 目录下的 21 个文件、10 个已发布 preset 文件，以及 26 个长期指令或发现入口；manifest 缺失数均为 0。`prompt-surface-scan.tsv` 与扩展发现规则选出的 125 条路径完全一致。 |
| 符号链接处理 | 5 个 `CLAUDE.md` 链接 blob 都是 `AGENTS.md`；`.claude/skills` 是 `../.agents/skills`。镜像将这些原始 blob 保存为普通 `.orig` 文件。审阅包中没有实际符号链接。 |
| 派生产物配对 | `ARTIFACT_INDEX.tsv` 包含 45 组英文／可执行产物与中文／说明对侧。每个目标和来源记录都存在；Markdown 标题层级和围栏代码一致；派生产物中的相对链接均可解析。 |
| 候选 Skill | 在隔离 Python 环境中，Skill Creator 的 `quick_validate.py` 对 7 份推广副本全部通过。7 个 `agents/openai.yaml.review` 均可解析，英文简介长度为 25–64 个字符，并引用正确的 `$skill-name`。 |
| 原文 fork 快照 | 12 个候选快照文件全部与固定上游逐字节一致，其中包括完整且独立的 `dsh-trim-cot-leakage` Skill、示例和召回检索式。 |
| Hook 和 CI 实现 | 3 个脚本均通过 Node 语法检查，hook 通过 `sh -n`，23 个 YAML 文件和 JSON 配置均可解析。门禁 smoke 的 5 个场景全部通过：暂存成功、暂存删除隔离、拒绝重命名受保护路径、拒绝单边投影变更，以及 base 到 HEAD 成功。 |
| 文本和发现隔离 | 派生文件都只有一个结尾换行且没有行尾空白。审阅包中不存在会生效的字面 `SKILL.md`、`AGENTS.md` 或 `CLAUDE.md`。`npx skills add /Users/jfmoe/Coder/skills --list` 仍只发现仓库原有的 11 个生效 Skill。 |
| 工作区边界 | 本任务的所有路径都位于 `docs/research/ai-coding-context-kit-review/`。该目录之外唯一的状态项是用户原有的 `registry/ledger.yaml`；其 Git blob 始终为 `5e3725a3f8b21b5d6466ebd74d44605a2b1fc1dc`。 |

## 自审中修正的发现

- 扩展发现规则找到了初始文件名规则遗漏的 5 个生效 `CLAUDE.md` 符号链接和 `.claude/skills` Skill 发现链接。它们现已进入镜像、分类和校验器；最终数量为 70 个来源、125 条扫描路径。
- “fail closed”的中文曾错误使用另一个概念“快速失败”。安全指令和两份审计表中已统一改为默认拒绝。
- 来源与产物对照发现三条测试规则在候选提示词中表达不足：过时行为应与测试同步修改、未覆盖代码可能是死代码，以及同进程类型边界不应测试不可能的敌意输入。它们现已明确进入项目／测试指令及简化、review、检查选择 Skill。
- `dsh-trim-cot-leakage` 保持为完整、独立的候选单元：Skill、UI 元数据、示例、召回检索式、对应中文文件和双语来源记录；3 个上游原文文件也单独保存。
- 确认旧版 `project/`、`skills/`、`user/` 和 `registry/` 目录树不含文件后，已删除这些空目录。

## 剩余人工审核边界

机械检查不能证明某项通用政策一定适合具体目标仓库，也不能证明每处翻译细节都达到最佳表达。推广前，人工审核应将每个候选产物与同目录 `SOURCES.md`、处置表、条款表和固定原文镜像对照。本次验证没有安装、启用、推广或提交审阅包中的任何候选内容。
