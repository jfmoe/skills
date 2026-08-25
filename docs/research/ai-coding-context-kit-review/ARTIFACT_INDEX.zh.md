# 产物索引

[English](ARTIFACT_INDEX.md) | 中文

规范映射位于 `ARTIFACT_INDEX.tsv`，共包含 45 组派生产物。每行记录：

- 规范英文产物或唯一可执行产物；
- 对应的简体中文翻译或中文说明；
- 列出精确上游路径和行号的来源记录；
- 校验器使用的配对类型。

`upstream/repository/` 下的原始文件和 `artifacts/registry/upstream/` 下的原文文件属于来源证据，不是派生产物。名为 `SOURCES.md` 的来源文件和与语言无关的 TSV 清单属于元数据，不是提示词交付物。

校验器会拒绝未登记的派生产物、缺失的对侧文件或来源记录、重复索引项、Skill 名称不匹配，以及标题层级或围栏代码不一致的 Markdown 对。
