# Sources for `security-sensitive/AGENTS.md`

Upstream: `deepseek-ai/deepseek-harness` at `47f943859bef60e4160492346772ded9b24f765a`. License notice: [`../../../THIRD_PARTY_NOTICES.md`](../../../THIRD_PARTY_NOTICES.md).

| Rule | Source and position | Preservation |
|---|---|---|
| Fail closed | `native/landlock-run/AGENTS.md`, lines 9-16; `docs/subsystems/approval.md`, lines 5-28 | Generalized from confinement and approval outcomes. |
| Enforce at the operation | `packages/AGENTS.md`, line 14; `docs/subsystems/approval.md`, lines 84-88 | Substantially verbatim. |
| Environment and temporary paths | `docs/defensive-patterns.md`, lines 27-29 | Substantially verbatim. |
| Link-shaped deletion | Same file, lines 31-33 | Generalized while preserving the safe operation. |
| Credential redirects | `packages/web/AGENTS.md`, line 5 | Generalized. |
| Alternate-caller negative control | `.agents/skills/dsh-code-review/SKILL.md`, lines 37 and 42 | Adapted. |

Sources:

- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/defensive-patterns.md#L27-L33>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/subsystems/approval.md#L5-L28>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/web/AGENTS.md#L1-L5>
