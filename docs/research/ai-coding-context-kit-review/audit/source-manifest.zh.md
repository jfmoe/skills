# 来源 manifest

[English](source-manifest.md) | 中文

规范清单位于 `source-manifest.tsv`，包含提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` 中 70 个互不重复的上游文件。

清单包括：

- 20 个 `AGENTS.md`：16 个生效指令文件和 4 个测试 fixture。
- 5 个生效的 `CLAUDE.md` 符号链接；每个链接 blob 都是 `AGENTS.md`，并解析到同目录指令文件，因此没有新增条款。
- 1 个生效的 `.claude/skills` 符号链接；链接 blob 是 `../.agents/skills`，它暴露相同的 11 个仓库 Skill，不新增 Skill 文本。
- 11 个仓库 Skill，以及各自目录中的全部 wrapper、reference 和脚本。
- 4 个已发布的 Agent 组合、4 个展示元数据文件和 2 个 preset 内置 Skill。
- 12 个直接相关的开发、测试、review、审批、Agent Note 和翻译政策文件。
- 上游 MIT 许可证。

每行记录原始路径、安全镜像路径、Git blob SHA、行数、来源类别和唯一处置结果。校验器会拒绝重复原始路径、重复镜像路径、缺失镜像、哈希不符、未知处置值，以及镜像中可能触发发现机制的文件名。

`prompt-surface-scan.tsv` 定义范围更广的发现边界，共记录 125 条按路径发现的候选项，包括已识别的 Agent 指令和 Skill 发现入口、`SKILL.md`、名称含 prompt/instruction 的文件，以及已发布的 preset 目录。70 个语料文件以外的路径也有明确分类：产品运行时、工具实现、测试／fixture、历史 Agent Note 或其他不适合移植的上下文。
