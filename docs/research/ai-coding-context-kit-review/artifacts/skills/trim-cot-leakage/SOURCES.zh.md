# 来源和通用化改动

[English](SOURCES.md) | 中文

## 精确上游来源

完整上游目录按提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` 独立保存：

- `.agents/skills/dsh-trim-cot-leakage/SKILL.md` 第 1–45 行；
- `.agents/skills/dsh-trim-cot-leakage/references/examples.md` 第 1–253 行；
- `.agents/skills/dsh-trim-cot-leakage/references/recall-batteries.md` 第 1–43 行。

完整命题补充来源：`.agents/skills/dsh-prose-standard/SKILL.md` 第 28–42 行。

## 保留的原文写法

定义、一条判断、全部八类分类、每项“不属于泄漏”例外、先改所有者的工作流、过度修正陷阱、示例和召回检索式全部保留。这是独立 Skill；没有其他产物能够替代它。

通用英文示例保留上游文字，只把链接改为固定提交或本地通用目标。召回命令保留检索式，只将 DeepSeek 专用排除项替换为目标范围占位符。

## 通用化改动

- 删除 DeepSeek Agent Note 名称、双语门禁命令和固定仓库排除项。
- 在 Git 上下文可能不同的位置，将“HEAD”通用化为“当前仓库状态”。
- 保留 issue、PR、抑制理由、反事实、测量、运行时状态、外部引用和文体例外。
- 新增 Skill、示例和召回检索式的完整简体中文翻译。
- `review-code-prose` 只提供命题保留前置规则；它不吸收本分类体系或工作流。

原文快照：`../../../upstream/repository/.agents/skills/dsh-trim-cot-leakage/SKILL.md.orig`，以及同目录两个 reference。
