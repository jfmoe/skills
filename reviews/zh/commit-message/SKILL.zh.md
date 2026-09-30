---
name: commit-message
description: 写 git 提交信息或提交改动。在用户要求提交、写提交信息或运行 /commit 时使用，以及 agent 提交自己的工作时使用。
---

# Commit Message

提交信息是一次改动的永久记录。日后的维护者和 agent 通过 `git log --grep` 和 `git blame` 找到它，再借此理解代码为什么是现在的样子。代码说明改了什么；提交信息承载代码无法表达的内容：为什么改，以及如何证明改动有效。

## 标题

使用 Conventional Commits：`<type>(<scope>): <summary>`，祈使语气，50 个字符左右。摘要要足够具体，让浏览历史的读者能把这个提交和其他提交区分开。

## 正文

只要改动的原因无法从 diff 中一眼看出，就写正文。正文写给当时不在场的读者，回答：

- 解决了什么问题，影响是什么？
- 为什么这是正确的修复？
- 它有哪些不足：代价是什么，没有覆盖什么？

读者需要的、来自关联 issue 或讨论的内容，要概括写进来，而不是只给链接。篇幅与改动相称，从一句话到几段不等。

原因从 diff 就能看出的小改动只写标题，例如格式化、错别字修正、重命名或细微的措辞调整。

正文只记录你知道的事，绝不猜测。提交不是你做的改动、且对话中没有给出原因时，只写标题。

## 验证

验证发生在 diff 之外时（手动检查、复现缺陷、测量、比对输出），在 `Test:` trailer 中记录下来：做了什么，以及结果如何。diff 中新增的测试本身就是证据，不需要 trailer。

其他 trailer 视情况使用：issue 用 `Refs: #123` 或 `Closes #123`，由已知提交引入的缺陷用 `Fixes: <sha> ("<subject>")`，破坏性变更用 `BREAKING CHANGE:`。

## 示例

```text
fix(ledger): keep pending proceeds out of cash

Sell proceeds were added to cash on the trade date, so the ledger
showed money that had not settled and allowed buys against it.
Proceeds now stay pending until settlement, matching how the broker
reports buying power. Same-day rebuys from sale proceeds are no longer
possible; the ledger has no margin model to support them.

Test: sold and rebought in dev; the rebuy was rejected until
  settlement
Refs: #214
```
