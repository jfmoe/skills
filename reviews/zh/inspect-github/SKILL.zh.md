---
name: inspect-github
description: 使用 gh CLI 读取和分析 GitHub 内容。当目标是任何托管在 GitHub 上的远程内容或仓库时使用。
---

# 检查 GitHub

使用 `gh` 命令作为访问 GitHub 内容的默认界面。

- 优先使用专用命令，如 `gh repo view`、`gh pr view`、`gh issue view` 和 `gh api`，而非未经认证的 HTTP 抓取。
- 进行仓库分析时，先用 `mktemp -d` 创建目录，再使用 `gh repo clone OWNER/REPO TEMP/REPO -- --depth 1` 浅克隆，然后检查本地检出。
- 仅在任务需要时才拉取额外的 ref 或历史记录。
