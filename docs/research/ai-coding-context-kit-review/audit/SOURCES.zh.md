# 审计产物来源

[English](SOURCES.md) | 中文

| 产物 | 来源 |
|---|---|
| `source-manifest.tsv` | 上游提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` 的 Git tree 和 blob 对象；语料边界来自已批准的重建计划。 |
| `prompt-surface-scan.tsv` | 对同一 Git tree 执行路径扫描，覆盖已识别的 Agent 指令文件名（包括 `AGENTS.md` 和 `CLAUDE.md`）、Skill 发现符号链接、全部 `SKILL.md`、名称含 prompt/instruction 的文件和已发布 preset 路径。 |
| `source-manifest*.md` | 两个 TSV 清单及其计算结果。 |
| `disposition-ledger*.md` | manifest 中全部生效 `AGENTS.md` 和 `CLAUDE.md`、仓库及 preset 内置 Skill、已发布 preset 和补充政策。 |
| `clause-ledger*.md` | 每个表格行明确列出的精确行号；行号不从派生产物反推。 |
| `scripts/verify-review-bundle.mjs` 及其中文说明 | 已批准重建计划中的完整性要求、Git tree／blob 格式、`skills/manage-skills/SKILL.md` 中的本地 Skill 发现限制，以及已根据固定 tree 证明的扩展指令／Skill／preset 发现规则。 |
| `scripts/smoke-agent-guardrails.mjs` 及其中文说明 | 候选项目校验器的行为接缝：精确暂存快照、重命名覆盖、规范源／投影配对、受保护路径和 base 到 HEAD 模式。 |
| `validation-report*.md` | 重建完成后实际运行命令得到的结果。 |

TSV 文件属于与语言无关的结构化证据；中英文说明文档是供人工阅读的对侧文件。
