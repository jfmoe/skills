# Agent guardrails CI 说明

[English implementation](agent-guardrails.yml)

该候选 GitHub Actions 工作流在每个 PR 上：

1. 获取完整 Git 历史，使基线提交可解析。
2. 对 PR 基线 SHA 到 `HEAD` 的结果差异运行 `git diff --check`。
3. 用同一个基线运行 `verify-agent-guardrails.mjs --base`。

工作流只读取仓库内容，权限为 `contents: read`。它不判断提示词或文档写得是否正确；语义质量仍由 review 负责。
