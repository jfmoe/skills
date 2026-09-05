---
name: implement-tickets-with-workers
description: 串行编排 worker subagent 实现一组 tickets。
disable-model-invocation: true
---

# Implement Tickets With Workers

## 调用会话：选择执行位置

如果当前工作目录存在相关的 ADR/CONTEXT 改动，先提交代码。

从当前上下文提取原始任务输入：工作目录绝对路径、当前分支和 HEAD、初始 Git 状态，以及全部 tickets 和父规格的路径。保留路径、标识符和 Git 输出的原文，不概括规格内容。

本次调用前已有至少两轮实质交互时，自动移交新会话；否则直接在当前会话读取 `NEW_SESSION_PROMPT.md`，使用上面记录的任务输入执行。工具调用、进度消息和简短路径澄清不计入轮次；tickets 在其他会话创建不构成移交理由。用户明确指定的会话安排优先，移交接收方不再次移交。

仅在需要移交时执行以下步骤。

若当前会话已位于某个 worktree，新会话使用同一工作目录绝对路径。只有能绑定该目录时才创建；否则向用户报告无法满足同 worktree 约束。

创建上下文独立的全新 Codex 会话，并只向其传入下面这段启动提示词；用上一步的原始值替换尖括号字段：

```text
在 <工作目录绝对路径> 中工作。打开并完整读取 <本 skill 目录绝对路径>/NEW_SESSION_PROMPT.md，将其全部内容作为唯一执行流程。

任务输入：
- 当前分支：<分支>
- 基线 HEAD：<HEAD>
- 初始 Git 状态：<git status --short 的原始输出；空状态明确写“空”>
- Tickets：<全部 ticket 路径，每行一个>
- 父规格：<全部父规格路径，每行一个>
```

启动提示词只承载上述定位指令和原始任务输入；静态执行流程以 `NEW_SESSION_PROMPT.md` 为单一事实来源。创建成功后，调用会话停在移交点，由新会话的主 Agent 继续。

完成标准：当前会话已进入执行流程，或新会话已绑定同一工作目录并能直接读取 `NEW_SESSION_PROMPT.md` 和全部原始任务输入。
