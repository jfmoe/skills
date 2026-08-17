# Sources for `user/AGENTS.md`

Upstream: `deepseek-ai/deepseek-harness` at `47f943859bef60e4160492346772ded9b24f765a`. License notice: [`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

| Prompt rule | Source and position | Preservation |
|---|---|---|
| Explore first; prefer existing patterns | `apps/cli/config/agent-presets/standard/agent.cordis.yml`, line 116 | First sentence and closing sentence preserved verbatim; mutation-specific middle clauses omitted for an always-on user default. |
| Resolve discoverable facts | Same file, line 120 | Preserved with the product tool name removed. |
| Avoid speculative scope | `packages/AGENTS.md`, lines 11-12; `.agents/skills/dsh-code-review/SKILL.md`, line 34 | Adapted into a cross-project preference. |
| Tests are evidence, not truth | `AGENTS.md`, lines 121-123; `.agents/skills/dsh-code-review/SKILL.md`, lines 16-17 | “Tests describe behavior, not correctness” is verbatim; the remaining evidence classes are generalized. |
| Narrowest credible check and no repetition | `AGENTS.md`, lines 86-92; `.agents/skills/dsh-pre-push-checks/SKILL.md`, lines 27-37 | Substantially preserved. |
| Environment failure versus project failure | `AGENTS.md`, lines 82-84; `.agents/skills/dsh-pre-push-checks/SKILL.md`, lines 83-90 | Generalized. |
| Report only commands run and remaining gaps | `AGENTS.md`, line 88; `.agents/skills/dsh-pre-push-checks/SKILL.md`, lines 83-113 | Adapted. |

Pinned links:

- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/apps/cli/config/agent-presets/standard/agent.cordis.yml#L113-L124>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/AGENTS.md#L82-L92>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/AGENTS.md#L119-L125>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-pre-push-checks/SKILL.md#L83-L113>
