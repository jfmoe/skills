# Sources for `verify-agent-guardrails.mjs`

Upstream: `deepseek-ai/deepseek-harness` at `47f943859bef60e4160492346772ded9b24f765a`. License notice: [`../../THIRD_PARTY_NOTICES.md`](../../THIRD_PARTY_NOTICES.md).

The script implementation is original. It mechanizes only rules the source project treats as objectively checkable:

| Check | Source and position | Extracted rule |
|---|---|---|
| Artifact/source companion exists in the exact index or HEAD snapshot | `docs/AGENTS.md`, lines 15-34; `.agents/skills/dsh-pre-push-checks/SKILL.md`, lines 10-25 | One owner per maintained fact; inspect the exact outgoing snapshot rather than allowing worktree-only files to satisfy it. |
| Explicit protected paths | `vendor/AGENTS.md`, lines 3-7; `.agents/notes/archived/AGENTS.md`, lines 3-7 | Frozen and vendored areas need an owning workflow rather than casual edits. |
| Projection changes accompany owners | `website/AGENTS.md`, lines 5-11; `.agents/skills/dsh-doc-site-sync/SKILL.md`, lines 8 and 21-27 | Edit canonical prose or generator, then regenerate disposable projections. |
| Gate only mechanical invariants | Root `AGENTS.md`, lines 137-141; `.agents/skills/dsh-code-review/SKILL.md`, lines 20-27 | Automated gates cannot establish semantic correctness; semantic review remains a Skill. |

Pinned links:

- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/AGENTS.md#L15-L45>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/website/AGENTS.md#L5-L11>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/AGENTS.md#L137-L141>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-doc-site-sync/SKILL.md#L8-L27>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-pre-push-checks/SKILL.md#L10-L25>

The script deliberately does not judge prose quality, architectural necessity, test sufficiency, security correctness, or whether a simplification is valid.

`--staged` reads the config and artifact set from the Git index; worktree-only files cannot satisfy a commit. `--base` reads them from `HEAD` and evaluates changed paths against the supplied merge base. `--all` validates the complete tracked index and config shape without pretending every tracked protected path changed.
