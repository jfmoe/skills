# Pre-commit 钩子说明

[English implementation](pre-commit)

该候选钩子只执行两个快速、基于暂存区的机械检查：

1. `git diff --cached --check`：拒绝暂存差异中的空白错误。
2. `node scripts/verify-agent-guardrails.mjs --staged`：检查受保护路径、规范源／投影组和伴随文件。

它不会运行测试、构建、文档语义 review 或完整质量门禁；相关检查由开发者根据改动面选择，穷尽检查交给 CI。启用前需要将钩子放到目标仓库并显式配置 `core.hooksPath`。
