# Sources for `agent-guardrails.yml`

Upstream: `deepseek-ai/deepseek-harness` at `47f943859bef60e4160492346772ded9b24f765a`. License notice: [`../../../THIRD_PARTY_NOTICES.md`](../../../THIRD_PARTY_NOTICES.md).

| Workflow behavior | Source and position | Preservation |
|---|---|---|
| CI owns exhaustive, cross-platform gates | Root `AGENTS.md`, lines 86-92; `.agents/skills/dsh-pre-push-checks/SKILL.md`, lines 6-8 | The separation between narrow local hooks and CI is preserved. This workflow itself remains narrow because it owns only agent-artifact mechanics. |
| Verify the live PR comparison | `.agents/skills/dsh-code-review/SKILL.md`, line 8; `.agents/skills/dsh-pre-push-checks/SKILL.md`, lines 19-25 | Uses the pull request's exact base SHA rather than a guessed branch name. |
| Checkout and Node actions | DeepSeek `.github/workflows/ci.yml`, representative lines 75-84 | `actions/checkout@v6`, `actions/setup-node@v6`, full history, and Node 22 follow the source project. |
| Shared mechanical verifier | Original implementation in this kit | CI calls the same policy engine as the hook. |

Sources:

- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.github/workflows/ci.yml#L75-L84>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-code-review/SKILL.md#L6-L8>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-pre-push-checks/SKILL.md#L19-L25>

This workflow does not claim to replace project tests, builds, linters, security tests, or semantic review.
