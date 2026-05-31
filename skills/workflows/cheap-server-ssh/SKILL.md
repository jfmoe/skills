---
name: cheap-server-ssh
description: Use when the user asks to connect to cheap_server.
---

# Cheap Server SSH

Use this skill for remote operations on the SSH host alias `cheap_server`.

## Required Workflow

1. Invoke `ssh` skill in the same turn and follow both skills together.
2. Ask user confirmation before connecting (example: "是否现在连接 cheap_server VPS？").
3. After user confirms, verify SSH alias availability.

```bash
rg '^Host\\s+cheap_server$' ~/.ssh/config
```

4. Start interactive connection immediately.

```bash
ssh cheap_server
```

5. After login succeeds, stop and wait for the user's next instruction.

## Optional Next Steps (Run Only After User Asks)

Use these only when the user gives a concrete remote task:

```bash
sed -n '1,260p' /root/AGENTS.md
date -u; TZ=Asia/Shanghai date
systemctl --user status cliproxyapi --no-pager | sed -n '1,40p'
journalctl --user -u cliproxyapi --since '30 minutes ago' --no-pager
```

## Failure Handling

If login fails:

1. Retry with verbose diagnostics.

```bash
ssh -vv cheap_server
```

2. If host key mismatch occurs, verify and fix with:

```bash
ssh-keygen -R 107.174.90.215
ssh-keygen -R cheap_server
```

3. Reconnect after confirmation from the user.

## Safety Rules

- Do not run destructive commands unless explicitly requested by the user.
- Do not run remote operational commands until the user provides the next instruction after login.
- Keep remote changes minimal and document what changed.
