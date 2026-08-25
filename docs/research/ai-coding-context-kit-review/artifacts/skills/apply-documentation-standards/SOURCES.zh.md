# 来源和通用化改动

[English](SOURCES.md) | 中文

## 精确上游来源

提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` 中的主要来源：

- `.agents/skills/dsh-doc-standards/SKILL.md` 第 8–56 行；
- `docs/AGENTS.md` 第 7–45、59–75 行；
- `.agents/skills/dsh-doc-site-sync/SKILL.md` 第 8–27、43–54 行；
- `.agents/notes/implemented/AGENTS.md` 第 5–13 行。

## 保留的原文写法

上游写作顺序、教程／参考区分、“每项事实只有一个真源”、当前状态规则、生成材料先改所有者、赘余分类和语义 review 边界均基本保留。

## 通用化改动

- 删除所有 Markdown 换行、字数预算、标题、双语配对、locale、VitePress、DeepSeek 文档层级名、Agent Note 格式和固定命令要求。
- 将固定层级表替换为语义角色，由目标仓库映射到自身层级。
- 根据用户要求加入明确的“不规定格式”边界。
- 将 `dsh-trim-cot-leakage` 作为 `trim-cot-leakage` 独立保留；本 Skill 只链接，不吸收其分类体系。
- 新增简体中文翻译，不加入格式政策。

原文快照：`../../../upstream/repository/.agents/skills/dsh-doc-standards/SKILL.md.orig`。
