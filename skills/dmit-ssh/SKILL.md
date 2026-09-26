---
name: dmit-ssh
description: 仅手动调用，连接 DMIT VPS 并读取远端运维规则。
disable-model-invocation: true
---

# DMIT SSH

先连接并读取远端规则：

```bash
ssh dmit 'cat "$HOME/AGENTS.md"'
```

收到并阅读完整输出后，再单独调用 SSH，按远端规则完成用户已授权的任务。规则缺失或不可读时，先报告情况。
