---
name: delegate-to-codex
description: 即将 spawn reviewer、explorer 或 researcher 时使用；走 codex exec 后台任务，429/5xx/网络错误回退本地 subagent
---

# 委派 Codex

## 判定

完成标准：已分成 **worker** 或 **launcher**；launcher 已确认环境。

本轮 brief 已含填实的产物路径和交接步骤 → **worker**：自己执行任务，写产物，按交接退出。

否则是 review / explore / research 委派 → **launcher**。环境检测：

```bash
command -v codex
```

失败则停：报告本环境无 codex CLI。

## 产物路径

完成标准：一条绝对路径。

原 skill 或用户已指定则用它；research 且仓库已有 notes 约定则走约定。否则：

```bash
mktemp /tmp/codex.XXXXXX
```

## 写 brief

完成标准：Goal / Context / Constraints / Done when / 交接 写全。交接协议以本节为唯一来源。

Brief = 原本要给 subagent 的内容 + 产物路径 + 交接模板，写入 `mktemp /tmp/codex-brief.XXXXXX`：

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
  1. 完整结果写入 <artifact>
  2. 最终回复只给一行结论（DONE 或 FAILED: <one-line>），不要重复全文
```

review 类 brief 加「评审口径」段：每条发现标注类型（事实冲突 / 规格缺口 / 改进建议）+ 证据（权威来源原文）；只报「不改会出错或返工」的，风格与可选增强单列「可选」区；修法聚焦实质改进（正确性、可读性、降复杂度），不带既定决策外的新机制。

## 启动

完成标准：后台任务已启动。

全权限 `--dangerously-bypass-approvals-and-sandbox`；一次性委派覆盖 `-c model_reasoning_effort="high"`。

模型按委派类型固定：`review` 使用 `gpt-6-astra`；`explore` 和 `research` 使用 `gpt-6-sol`。以下命令中的 `<model>` 必须按此映射填入，不继承默认模型。

用宿主后台任务跑 `codex exec`，长 timeout；长 brief 走 stdin，`-o` 兜底捕获最终消息：

```bash
codex exec -C "$PWD" --dangerously-bypass-approvals-and-sandbox \
  --model <model> \
  -c model_reasoning_effort="medium" \
  -o <artifact>.last - < "$BRIEF_FILE"
```

产物以 codex 写出的 `<artifact>` 为准，`<artifact>.last` 仅作最终消息兜底（`-o` 只存最后一条消息）。记下 task_id / artifact 供消费定位；启动即失败（任务秒退、stderr 报错）→ 按失败回退节分类处理。任务启动即收束本轮，回 idle 等完成通知；并行则 N 个后台任务、产物。

## 消费

完成标准：产物已读；review 已逐条裁定且裁定表已向用户汇报；其余类型已接回原 workflow。

后台任务完成通知即回呼等价物。exit 0 且 `<artifact>` 非空 → 按 DONE 处理，读完再裁定/接回；非零退出或产物为空 → 按失败回退节分类处理。

review 结果由 **launcher** 逐条裁定——reviewer 只产候选：

1. **先核验，再裁定**：finding 的事实主张先对权威来源（票 resolution、CONTEXT.md、代码）核验，不过则整条驳回。
2. **发现与修法分离**：发现属实 ≠ 修法照收。提高代码可读性、降复杂度的修法积极采纳；夹带新机制/新抽象、过度设计、罕见场景防御的降级（发现照收、修法从简）或驳回。

## 失败回退

完成标准：429/5xx/网络错误已由本地 subagent 接手；其余失败已向用户报告。

先从任务日志与 stderr 判定错误类别：

- **429 / 5xx / 网络错误**（含 rate limit、connection 类报错）：launcher 委派自己的 subagent 接手。brief = 写 brief 节的原任务内容（review 含评审口径）。`<artifact>` 已有部分内容 → **续接**：subagent 先读 `<artifact>`，续写至完成；产物为空或不存在 → **执行**：subagent 从头产出。完整结果写入 `<artifact>`，完成后回消费节读产物裁定/接回。
- **其余失败**（认证错误、CLI 自身错误、超时等）：补读 `<artifact>.last` 与任务日志，报告用户并停。

## 清理

完成标准：brief 临时文件已删除。

```bash
rm -f "$BRIEF_FILE"
```
