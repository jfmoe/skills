# 来源和通用化改动

[English](SOURCES.md) | 中文

## 精确上游来源

主要来源：提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` 中 `.agents/skills/dsh-prose-standard/SKILL.md` 第 8–81 行。

补充来源：

- `docs/AGENTS.md` 第 36–45、59–75 行；
- 根目录 `AGENTS.md` 第 137–143 行；
- `examples/AGENTS.md` 第 16–18 行；
- 上游示例 `.agents/skills/dsh-prose-standard/references/examples.md` 第 1–167 行。

## 保留的原文写法

完整命题规则、局部约定规则、按文字位置确定必要覆盖、工作流分类和边界情况定义均大体保留上游写法。英文示例逐字复制。

## 通用化改动

- 删除对 DeepSeek `vendor/` 和已归档 note 的无条件排除；通用 Skill 遵守目标仓库的受保护路径规则。
- 删除 DeepSeek 双语配对、Agent Note 格式、包 README 模板、固定命令、PR 渠道机制和把学到的规则写回 reference 的行为。
- 将原来缺少 `scope` 时硬停止，改为根据点名文件、当前差异或明确路径建立安全边界。
- 独立保留 `trim-cot-leakage` 并链接到它，不再把其分类体系压缩为 prose 子章节。
- 新增 Skill 和示例的简体中文翻译，不增加命题。

原文快照：`../../../upstream/repository/.agents/skills/dsh-prose-standard/SKILL.md.orig`；示例为镜像中同目录的 `references/examples.md`。
