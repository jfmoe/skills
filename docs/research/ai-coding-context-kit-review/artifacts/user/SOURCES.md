# Sources for user-level instructions

English | [中文](SOURCES.zh.md)

Unless stated otherwise, every upstream path and line range refers to `deepseek-ai/deepseek-harness` commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`.

| Candidate clause | Exact source | Treatment |
|---|---|---|
| Explore first; resolve discoverable facts; ask only for user-owned choices | `apps/cli/config/agent-presets/standard/agent.cordis.yml` lines 116, 120–124 | Retained with product tool names removed. |
| Require a current owner, need, consumer, and evidence for public choices | `packages/AGENTS.md` lines 10–12 | Retained and generalized. |
| Prefer existing patterns and avoid speculative scope | `apps/cli/config/agent-presets/standard/agent.cordis.yml` line 116; `.agents/skills/dsh-code-review/SKILL.md` lines 33–35 | Retained and generalized. |
| Run the narrowest credible evidence once | Root `AGENTS.md` lines 87–93; `.agents/skills/dsh-pre-push-checks/SKILL.md` lines 27–37, 62–64 | Retained without DeepSeek commands or push mechanics. |
| Verify review claims on technical grounds | `.agents/skills/dsh-code-review/SKILL.md` line 49; `docs/cookbook/responding-to-pr-review-on-a-stack.md` lines 17–24 | Retained and generalized. |
| Report scope, assumptions, changes, checks, and gaps | `.agents/skills/dsh-prose-standard/SKILL.md` lines 65–71; `.agents/skills/dsh-pre-push-checks/SKILL.md` lines 83–92 | Adapted. |

The Chinese file translates the candidate clauses; it does not add policy.
