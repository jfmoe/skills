---
name: delegate-to-codex
description: 即将 spawn reviewer、explorer 或 researcher 时使用
---

# 委派 Codex

## 判定

完成标准：已分成 **worker** 或 **launcher**，且 launcher 已确认 `HERDR_ENV=1`。

本轮 brief 已含填实的产物路径和交接步骤 → **worker**：自己执行任务，写产物，按交接退出。

否则是 review / explore / research 委派 → **launcher**。先：

```bash
test "${HERDR_ENV:-}" = 1
```

失败则停：本 skill 只在 Herdr 中可用。

## 产物路径

完成标准：一条绝对路径。

原 skill 或用户已指定则用它；research 且仓库已有 notes 约定则走约定。否则：

```bash
mktemp /tmp/codex.XXXXXX
```

## 写 brief

完成标准：Goal / Context / Constraints / Done when 写全，交接填好。交接协议以本节为唯一来源。

Brief = 原本要给 subagent 的内容 + 产物路径 + 下列模板，写入 `mktemp /tmp/codex-brief.XXXXXX`：

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

`<kind>` 为 `review` / `explore` / `research`；`<PARENT_PANE>` 为启动时的 `$HERDR_PANE_ID`。

review 类 brief 加「评审口径」段：每条发现标注类型（事实冲突 / 规格缺口 / 改进建议）+ 证据（权威来源原文）；只报「不改会出错或返工」的，风格与可选增强单列「可选」区；修法聚焦实质改进（正确性、可读性、降复杂度），不带既定决策外的新机制。

## 启动

完成标准：prompt 已送出。

全权限 `--dangerously-bypass-approvals-and-sandbox`；一次性委派覆盖 `-c model_reasoning_effort="medium"`。当前 workspace 新建 tab：

```bash
herdr agent list
herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --label <codex-review|codex-explore|codex-research> --no-focus
```

从返回 JSON 取 root pane id；name 用 `codex-review` / `codex-explore` / `codex-research`（匹配 `[a-z][a-z0-9_-]{0,31}`，撞名加后缀）。

```bash
herdr agent start <name> --kind codex --pane <root-pane-id> -- --dangerously-bypass-approvals-and-sandbox -c model_reasoning_effort="medium"
herdr agent prompt <name> "$(cat "$BRIEF_FILE")"
```

记下 `tab_id` / name / artifact 供消费定位；`agent start` 或 `prompt` 失败则 `herdr tab close <tab_id>`，报告 stderr 并停。prompt 送出即收束本轮，回 idle 接回呼；并行则 N 个 tab、产物、ping。

## 消费

完成标准：产物已读；review 已逐条裁定且裁定表已向用户汇报；其余 kind 已接回原 workflow。

以 `交接` 开头的回呼走本节。`交接 DONE`：产物非空则读完再裁定/接回；`交接 FAILED`：以回呼一行为结果，产物存在则补读。然后关本次 tab。

review 结果由 **launcher** 逐条裁定——reviewer 只产候选：

1. **先核验，再裁定**：finding 的事实主张先对权威来源（票 resolution、CONTEXT.md、代码）核验，不过则整条驳回。
2. **发现与修法分离**：发现属实 ≠ 修法照收。提高代码可读性、降复杂度的修法积极采纳；夹带新机制/新抽象、过度设计、罕见场景防御的降级（发现照收、修法从简）或驳回。

## 清理

完成标准：本次创建的 Herdr tab 已关。

```bash
herdr tab close <tab_id>
```
