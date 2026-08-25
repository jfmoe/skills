# 候选 fork 快照来源

[English](SOURCES.md) | 中文

本目录中的每个原文文件都从提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` 逐字节复制。来源与目标映射如下：

| 候选项 | 上游路径 |
|---|---|
| plan-code-changes | `apps/cli/config/agent-presets/standard/agent.cordis.yml` |
| audit-code-simplifications | `.agents/skills/dsh-find-simplifications/**` |
| review-code-changes | `.agents/skills/dsh-code-review/**` |
| select-relevant-checks | `.agents/skills/dsh-pre-push-checks/**` |
| apply-documentation-standards | `.agents/skills/dsh-doc-standards/**` |
| review-code-prose | `.agents/skills/dsh-prose-standard/**` |
| trim-cot-leakage | `.agents/skills/dsh-trim-cot-leakage/**` |

每个 `meta.yaml` 都遵循本地 `manage-skills` Skill 中的 fork schema。中文对侧文件解释相同字段，但不会作为 registry 输入。
