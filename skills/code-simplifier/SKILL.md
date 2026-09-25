---
name: code-simplifier
description: Simplifies and refines code for clarity, consistency, and maintainability while preserving all functionality. Focuses on recently modified code unless instructed otherwise. Runs in one subagent.
---

<!-- Modified from Anthropic's code-simplifier agent. -->

Run simplification in one fresh `worker` subagent. The parent owns scope and acceptance; the worker edits and verifies the code.

If you are already the worker assigned this simplification, read [references/simplifier.md](references/simplifier.md) and execute it directly. Do not delegate again.

1. Establish the target: the user's explicit scope, or the current task's changes, including relevant staged, unstaged, and untracked files. Record the current state so unrelated user changes remain protected.
2. Use `spawn_agent` with `agent_type="worker"` and `fork_turns="none"`. Give it a self-contained brief with the repository path, exact writable scope, exclusions, target changes, behavior to preserve, applicable instructions, and known checks. Include the absolute path to `references/simplifier.md` and require the worker to read it in full. Authorize the scoped edits and verification; forbid further delegation. If subagents are unavailable, report the limitation instead of simplifying in the parent.
3. Wait for the worker to finish using the session's waiting rules. Continue only independent work; do not edit the worker's files or repeat its investigation.
4. Inspect the resulting diff and verification evidence. Return concrete gaps to the same worker within the original scope. Report the accepted changes, checks, and unresolved gaps. No worthwhile simplification is a valid result.
