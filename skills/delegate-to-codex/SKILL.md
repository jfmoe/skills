---
name: delegate-to-codex
description: 即将 spawn reviewer、explorer 或 researcher 时使用
---

# 委派 Codex

review / explore / research 的 spawn 走 Codex

## 判定

完成标准：已分成 **worker** 或 **launcher**，且 launcher 已确认 `HERDR_ENV=1`。

本轮 brief 已含填实的产物路径和交接步骤 → **worker**：自己执行任务，写产物，按交接退出。

否则，任务是 review / explore / research 委派 → **launcher**。先：

```bash
test "${HERDR_ENV:-}" = 1
```

失败则停，说明本 skill 只在 Herdr 中可用。通过则进入下一步。

## 产物路径

完成标准：一条绝对路径。

原 skill 或用户已指定则用它。research 且仓库已有 notes 约定则走约定。否则：

```bash
mktemp /tmp/codex.XXXXXX
```

## 写 brief

完成标准：Goal / Context / Constraints / Done when 写全，交接填好。交接协议以本节为唯一来源。

Brief = 原本要给 subagent 的内容 + 产物路径 + 下列模板。写入 `mktemp /tmp/codex-brief.XXXXXX`，再交给启动命令。

```text
Goal:
<原任务>
Context:
<原上下文>
Constraints:
自己执行，禁止把任务再委派出去。
产物: <artifact>
Done when:
<原任务可观察的完成标准>
交接:
  把 `$HERDR_BIN_PATH` 当 PATH 里的二进制，用 shell 直接跑下列命令。禁止读取 herdr skill，禁止跑 --help 做发现。
  1. 完整结果写入 <artifact>
  2. "$HERDR_BIN_PATH" agent prompt <PARENT_PANE> "交接 DONE <kind> <artifact>"
     失败则 "$HERDR_BIN_PATH" agent prompt <PARENT_PANE> "交接 FAILED <kind> <artifact>: <one-line>"
  3. 无论 DONE 或 FAILED，接着 "$HERDR_BIN_PATH" agent prompt "$HERDR_PANE_ID" "/exit"
     进程仍在则 SIGTERM 父进程
```

`<kind>` 为 `review` / `explore` / `research`。`<PARENT_PANE>` 为启动时的 `$HERDR_PANE_ID`。

## 启动

完成标准：prompt 已送出。

全权限：`--dangerously-bypass-approvals-and-sandbox`。一次性委派覆盖 `-c model_reasoning_effort="medium"`。当前 workspace 新建 tab。

```bash
herdr agent list
herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --label <codex-review|codex-explore|codex-research> --no-focus
```

从返回 JSON 读取 root pane 的 pane id。name 用 `codex-review` / `codex-explore` / `codex-research`，须匹配 `[a-z][a-z0-9_-]{0,31}`；与 list 撞名则加后缀。

```bash
herdr agent start <name> --kind codex --pane <root-pane-id> -- --dangerously-bypass-approvals-and-sandbox -c model_reasoning_effort="medium"
herdr agent prompt <name> "$(cat "$BRIEF_FILE")"
```

`tab create` 之后立刻记下 `tab_id`。`agent start` 或 `prompt` 失败则 `herdr tab close <tab_id>`，报告 stderr 并停。

prompt 送出即收束本轮，回到 idle 接回呼。并行则 N 个 tab、N 个产物、N 条 ping。记下 tab / name / artifact，消费后关 tab。

## 消费

完成标准：产物已读；review 已逐条裁定；其余 kind 已接回原 workflow。

以 `交接` 开头的回呼走本节。`交接 DONE`：产物非空则读完再裁定/接回。`交接 FAILED`：以回呼一行为结果，产物存在则补读。然后关本次 tab。

review 结果由 **launcher** 逐条裁定，积极采纳真实缺陷，规格缺口，有利于代码质量、可读性、降低复杂度的建议。不采纳过度设计、罕见场景的防御性编程。

## 清理

完成标准：本次创建的 Herdr tab 已关。

```bash
herdr tab close <tab_id>
```
