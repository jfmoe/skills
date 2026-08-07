# 新会话执行提示词

你是本轮实现的主 Agent。以启动提示词中的工作目录和 Git 基线为 fixed point，直接执行本文件，不依赖调用会话补充或转述流程。

## 1. 校验并读取输入

确认当前工作目录、分支、HEAD 和 `git status --short` 与启动提示词一致。随后完整读取全部 tickets、父规格、相关评论和 blocking edges；依赖关系以 tracker 记录为准。基线不一致或输入路径不可读时，向用户报告精确差异并停在验收点。

完成标准：Git 基线逐项一致，且每个 ticket 的规格、父规格、评论和 blocking edges 均已读取。

## 2. 排定顺序

排出 blockers 先于 dependents 的串行顺序。

完成标准：每个 ticket 恰好出现一次，且它的所有 blockers 均位于其前方。

## 3. 串行委派

按顺序逐个以 `agent_type="worker"` 创建 fresh worker subagent，每次只运行一个。逐项替换下面模板中的尖括号字段，保持其余文字不变，并将完整模板作为 directive：

```text
在 `<工作目录绝对路径>` 中完成 ticket `<当前 ticket 路径>`。

完整读取该 ticket、它引用的父规格、相关评论和 blocking edges，实现该 ticket 所描述的工作。

尽可能在预先约定的接缝处使用 `$tdd`。定期运行类型检查和单个测试文件，完整测试套件只在最后运行一次。

完成后使用 `$code-review` 审查工作，你已获明确授权，可遵循 `$code-review` 流程继续派生 reviewer subagent，但不得将探索或实现工作委派给下级 subagent。

修改前记录当前 HEAD 作为 fixed point。实现和测试后，review fixed point 到当前工作区的全部未提交改动，包括 staged、unstaged 和 untracked 内容；处理 review 结果后，将工作提交到当前分支并关闭该 ticket。
```

等待当前 worker 及其下级 subagents 完整返回后，默认信任其产物、验证结果与 commit。commit 缺失、测试或 review 报告失败，或产物明确违背 ticket 验收项时，让同一 worker subagent 续接补完；如果 ticket 因为客观原因无法完成、或明确需要人来验收或参与，停止并向用户报告，否则进入下一 ticket。

完成标准：每个 directive 均由固定模板生成且没有未替换字段；每个 ticket 均由 worker 按上述内嵌实现流程完成并提交，执行顺序与 blocking edges 一致，且下一 worker 仅在前一 worker 完整返回后启动。

## 4. 主 Agent 收尾

汇总每个 ticket 的 commit、worker 验证结果和遗留风险，确认 commit 链及仓库状态。以 worker 的 review 和全量测试为验收证据；证据缺失或存在高风险疑点时补充验证。向用户报告并停在验收点，把合并或清理留到用户验收后的下一步。

完成标准：报告能逐 ticket 追溯 commit 和验证结果，仓库未提交状态与新会话创建前一致，用户拥有验收所需信息。
