---
name: commit-message
description: Write a git commit message or commit changes. Use when the user asks to commit, write a commit message, or runs /commit, and when the agent commits its own work.
---

# Commit Message

A commit message is the permanent record of a change. Future maintainers and agents find it through `git log --grep` and `git blame`, then use it to understand why the code looks the way it does. The code shows what changed; the message carries what the code cannot: why, and how the change was proven.

## Subject

Use Conventional Commits: `<type>(<scope>): <summary>`, in the imperative mood, around 50 characters. Make the summary specific enough that a reader skimming history can tell this commit apart from others.

## Body

Write a body whenever the reason for the change is not plain from the diff. Write it for a reader who was not there; it answers:

- What problem does this solve, and what is its impact?
- Why is this the right fix?
- What are its shortcomings: what does it cost or leave out?

Carry in anything from a linked issue or discussion that the reader needs, summarized rather than only linked. Scale the length to the change, from one sentence to a few paragraphs.

Small changes whose reason is plain from the diff, such as formatting, typo fixes, renames, or a minor wording tweak, take the subject alone.

The body records what you know, never a guess. When committing changes you did not make and the conversation does not give the reason, write the subject only.

## Verification

When verification happened outside the diff (a manual check, a reproduced bug, a measurement, a compared output), record it in a `Test:` trailer: what was done and what it showed. Tests added in the diff are their own evidence and need no trailer.

Other trailers as they apply: `Refs: #123` or `Closes #123` for issues, `Fixes: <sha> ("<subject>")` for a defect introduced by a known commit, `BREAKING CHANGE:` for breaking changes.

## Example

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
