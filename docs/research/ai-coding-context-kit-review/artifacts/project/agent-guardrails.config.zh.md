# Agent 门禁配置说明

[English implementation](agent-guardrails.config.json)

该 JSON 是候选项目门禁的唯一可执行配置；本文件是中文说明，不会被脚本读取。

- `protectedPaths`：禁止改动的精确文件或目录前缀。目录以 `/` 结尾，例如 `vendor/`。
- `sourceProjectionGroups`：必须一起变更的一组规范源和生成投影。每项格式为 `{"source":"path","projections":["path"]}`。任一成员发生变化时，规范源和所有投影都必须变化并存在于目标快照中。
- `requiredCompanions`：必须存在的产物／伴随文件对。每项格式为 `{"artifact":"path","companion":"path","updateTogether":true}`。当任一侧变化时，两侧都必须存在；`updateTogether` 为 `true` 时还要求同时变化。

空数组是安全默认值，不会假装目标仓库存在某种结构。推广到真实项目时，应只填写该项目确实拥有的不变量。
