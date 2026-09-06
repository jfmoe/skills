---
name: delegate-to-codex
description: 即将 spawn reviewer、explorer 或 researcher 时使用；Herdr 内走 tab 回呼，其他终端走 codex exec 后台任务
---

# 委派 Codex

## 判定

完成标准：已分成 **worker** 或 **launcher**；launcher 已确认环境并选定分支。

本轮 brief 已含填实的产物路径和交接步骤 → **worker**：自己执行任务，写产物，按交接退出。

否则是 review / explore / research 委派 → **launcher**。环境检测定分支：

```bash
test "${HERDR_ENV:-}" = 1
```

通过 → **Herdr 分支**。否则 `command -v codex` 通过 → **Direct 分支**。都失败则停：报告本环境既无 Herdr 也无 codex CLI。

## 产物路径

完成标准：一条绝对路径。

原 skill 或用户已指定则用它；research 且仓库已有 notes 约定则走约定。否则：

```bash
mktemp /tmp/codex.XXXXXX
```

## 写 brief

完成标准：Goal / Context / Constraints / Done when 写全，交接按分支填好。交接协议以本节为唯一来源。

Brief = 原本要给 subagent 的内容 + 产物路径 + 对应分支的交接模板，写入 `mktemp /tmp/codex-brief.XXXXXX`。共用头部：

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
```

Herdr 分支交接：

```text
交接:
  把 `$HERDR_BIN_PATH` 当 PATH 里的二进制，用 shell 直接跑下列命令。禁止读取 herdr skill，禁止跑 --help 做发现。
  1. 完整结果写入 <artifact>
  2. "$HERDR_BIN_PATH" agent prompt <PARENT_PANE> "交接 DONE <kind> <artifact>"
     失败则 "$HERDR_BIN_PATH" agent prompt <PARENT_PANE> "交接 FAILED <kind> <artifact>: <one-line>"
  3. 无论 DONE 或 FAILED，接着 "$HERDR_BIN_PATH" agent prompt "$HERDR_PANE_ID" "/exit"
     进程仍在则 SIGTERM 父进程
```

Direct 分支交接：

```text
交接:
  1. 完整结果写入 <artifact>
  2. 最终回复只给一行结论（DONE 或 FAILED: <one-line>），不要重复全文
```

`<kind>` 为 `review` / `explore` / `research`；`<PARENT_PANE>` 为启动时的 `$HERDR_PANE_ID`（仅 Herdr 分支）。

review 类 brief 加「评审口径」段：每条发现标注类型（事实冲突 / 规格缺口 / 改进建议）+ 证据（权威来源原文）；只报「不改会出错或返工」的，风格与可选增强单列「可选」区；修法聚焦实质改进（正确性、可读性、降复杂度），不带既定决策外的新机制。

## 启动

完成标准：任务已发出（Herdr：prompt 已送出；Direct：后台任务已启动）。

全权限 `--dangerously-bypass-approvals-and-sandbox`；一次性委派覆盖 `-c model_reasoning_effort="medium"`。

### Herdr 分支

当前 workspace 新建 tab：

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

### Direct 分支

用宿主后台任务跑 `codex exec`，长 timeout；长 brief 走 stdin，`-o` 兜底捕获最终消息：

```bash
codex exec -C "$PWD" --dangerously-bypass-approvals-and-sandbox \
  -c model_reasoning_effort="medium" \
  -o <artifact>.last - < "$BRIEF_FILE"
```

产物以 codex 写出的 `<artifact>` 为准，`<artifact>.last` 仅作最终消息兜底（`-o` 只存最后一条消息）。记下 task_id / artifact 供消费定位；启动即失败（任务秒退、stderr 报错）则报告 stderr 并停。任务启动即收束本轮，回 idle 等完成通知；并行则 N 个后台任务、产物。

## 消费

完成标准：产物已读；review 已逐条裁定且裁定表已向用户汇报；其余 kind 已接回原 workflow。

- Herdr 分支：以 `交接` 开头的回呼走本节。`交接 DONE`：产物非空则读完再裁定/接回；`交接 FAILED`：以回呼一行为结果，产物存在则补读。然后关本次 tab。
- Direct 分支：后台任务完成通知即回呼等价物。exit 0 且 `<artifact>` 非空 → 按 DONE 处理，读完再裁定/接回；非零退出或产物为空 → 按 FAILED 处理，补读 `<artifact>.last` 与任务日志。

review 结果由 **launcher** 逐条裁定——reviewer 只产候选：

1. **先核验，再裁定**：finding 的事实主张先对权威来源（票 resolution、CONTEXT.md、代码）核验，不过则整条驳回。
2. **发现与修法分离**：发现属实 ≠ 修法照收。提高代码可读性、降复杂度的修法积极采纳；夹带新机制/新抽象、过度设计、罕见场景防御的降级（发现照收、修法从简）或驳回。

## 清理

完成标准：分支资源已释放。

- Herdr 分支：

```bash
herdr tab close <tab_id>
```

- Direct 分支：删除 brief 临时文件；无 tab 可关。
