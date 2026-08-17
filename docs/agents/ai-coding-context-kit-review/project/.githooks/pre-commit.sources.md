# Sources for `.githooks/pre-commit`

Upstream: `deepseek-ai/deepseek-harness` at `47f943859bef60e4160492346772ded9b24f765a`. License notice: [`../../THIRD_PARTY_NOTICES.md`](../../THIRD_PARTY_NOTICES.md).

| Hook behavior | Source and position | Preservation |
|---|---|---|
| Staged whitespace/error check | Root `AGENTS.md`, lines 128-129 | `git diff --cached --check` is copied verbatim. |
| Keep hooks narrow | Root `AGENTS.md`, lines 86-92; `.agents/skills/dsh-pre-push-checks/SKILL.md`, lines 6-8 | Preserved as architecture: hook runs mechanical checks; semantic and exhaustive verification stay elsewhere. |
| Shared verifier | Original implementation in this kit | Prevents local and CI policy drift. |

Sources:

- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/AGENTS.md#L86-L92>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/AGENTS.md#L128-L129>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-pre-push-checks/SKILL.md#L6-L8>
