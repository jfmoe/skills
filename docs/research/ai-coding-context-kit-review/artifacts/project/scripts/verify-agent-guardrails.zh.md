# Agent 门禁校验器说明

[English implementation](verify-agent-guardrails.mjs)

该脚本读取目标仓库根目录下的 `agent-guardrails.config.json`，检查准确的 Git 快照，而不是混用工作区文件：

- `--staged`：读取暂存区 diff，并通过 `:path` 检查暂存区文件。
- `--base <revision>`：比较指定基线与 `HEAD`，并通过 `HEAD:path` 检查结果文件。
- `--config <path>`：覆盖默认配置路径。

脚本同时记录 rename／copy 的旧路径和新路径，因此不能通过重命名绕过受保护路径。它拒绝：

- 改动配置中的受保护路径；
- 只修改规范源／投影组的一部分；
- 组内文件在目标快照中缺失；
- 所需产物或伴随文件缺失；
- 配置要求同步更新时只修改其中一侧；
- 无效参数或无效配置。

退出码 `0` 表示通过，`1` 表示规则失败，`2` 表示调用或配置错误。
