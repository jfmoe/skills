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

可执行行为变更尽可能在预定接缝使用 `$tdd`；纯文档或提示词只做适用的产物检查。仅运行当前 ticket 相关的测试和局部检查，完整测试套件留给主 Agent 收尾。

完成后使用 `$code-review` 审查工作，你已获明确授权，可遵循 `$code-review` 流程继续派生 reviewer subagent，但不得将探索或实现工作委派给下级 subagent。

修改前记录当前 HEAD 作为 fixed point。实现和测试后，review fixed point 到当前工作区的全部未提交改动，包括 staged、unstaged 和 untracked 内容；处理 review 结果后，将工作提交到当前分支并关闭该 ticket。
```

等待当前 worker 及其下级 subagents 完整返回后，只确认 commit 存在、报告的验证和 review 成功且无 blocker，记录结果后进入下一 ticket；diff 审查、复测和逐项验收留到全部 worker 完成后。未通过交接门槛时，让同一 worker 续接补完；ticket 客观上无法完成或需人参与时，停止并报告。

完成标准：每个 directive 均由固定模板生成且没有未替换字段；每个 ticket 均由 worker 按上述内嵌实现流程完成并提交，执行顺序与 blocking edges 一致；下一 worker 仅在前一 worker 完整返回并通过交接门槛后启动，主 Agent 在 worker 间仅执行该门槛。

## 4. 主 Agent 收尾

全部 worker 完成后，主 Agent 审查初始 Git 基线后的最终 diff，逐 ticket 对照已读取的输入和验收项，检查最终行为、跨 ticket 集成、commit 链和仓库状态；worker 报告仅作线索。

发现问题由主 Agent 直接修复、针对性验证并提交，不再交还 worker。已知问题解决后运行完整测试套件；失败则修复并重跑至通过。

汇总各 ticket 的 commit、验证结果和遗留风险，向用户报告并停在验收点；合并或清理留到用户验收后。

完成标准：主 Agent 已验收每个 ticket 及跨 ticket 行为，修复已提交，完整测试通过，未提交状态恢复到新会话前，且报告可逐 ticket 追溯 commit 和验证结果。
