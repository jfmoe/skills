# Sources and portable changes

English | [中文](SOURCES.zh.md)

## Exact upstream source

The complete upstream directory is preserved independently at commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`:

- `.agents/skills/dsh-trim-cot-leakage/SKILL.md`, lines 1–45;
- `.agents/skills/dsh-trim-cot-leakage/references/examples.md`, lines 1–253;
- `.agents/skills/dsh-trim-cot-leakage/references/recall-batteries.md`, lines 1–43.

Supporting complete-proposition source: `.agents/skills/dsh-prose-standard/SKILL.md` lines 28–42.

## Preserved wording

The definition, one test, all eight taxonomy classes, every “not leakage” exception, owner-first workflow, overcorrection traps, examples, and recall batteries are retained. This is an independent Skill; no other artifact substitutes for it.

The portable English examples copy the upstream prose with only links changed to commit-pinned or local portable targets. Recall commands retain their probes while replacing DeepSeek-specific exclusions with target-scope placeholders.

## Portable changes

- Removed DeepSeek Agent Note names, bilingual gate commands, and fixed repository exclusions.
- Generalized “HEAD” to the current repository state where the exact Git context may differ.
- Retained issue, PR, suppression, counterfactual, measurement, runtime-state, external-reference, and genre exceptions.
- Added complete Simplified Chinese translations of the Skill, examples, and recall batteries.
- `review-code-prose` is only a prerequisite for proposition preservation; it does not absorb this taxonomy or workflow.

Pristine source: `../../../upstream/repository/.agents/skills/dsh-trim-cot-leakage/SKILL.md.orig` with both adjacent references.
