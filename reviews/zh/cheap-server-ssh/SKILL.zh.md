---
name: cheap-server-ssh
description: 当用户要求连接 cheap_server 时使用。
---

# Cheap Server SSH

对 SSH 主机别名 `cheap_server` 执行远程操作时，使用本 skill。

## 必需流程

1. 在同一轮中调用 `ssh` skill，并同时遵循两个 skill 的要求。
2. 连接前先向用户确认（示例："是否现在连接 cheap_server VPS？"）。
3. 用户确认后，验证 SSH 别名是否可用。

```bash
rg '^Host\\s+cheap_server$' ~/.ssh/config
```

4. 立即开始交互式连接。

```bash
ssh cheap_server
```

5. 登录成功后，停下来等待用户的下一条指令。

## 可选后续步骤（仅在用户提出要求后执行）

仅当用户给出具体的远程任务时才使用以下命令：

```bash
sed -n '1,260p' /root/AGENTS.md
date -u; TZ=Asia/Shanghai date
systemctl --user status cliproxyapi --no-pager | sed -n '1,40p'
journalctl --user -u cliproxyapi --since '30 minutes ago' --no-pager
```

## 失败处理

如果登录失败：

1. 使用详细诊断输出重试。

```bash
ssh -vv cheap_server
```

2. 如果出现主机密钥不匹配，用以下命令验证并修复：

```bash
ssh-keygen -R 107.174.90.215
ssh-keygen -R cheap_server
```

3. 经用户确认后重新连接。

## 安全规则

- 除非用户明确要求，否则不要运行破坏性命令。
- 登录后，在用户给出下一条指令之前，不要运行远程操作命令。
- 远程改动保持最小化，并记录所做的更改。
