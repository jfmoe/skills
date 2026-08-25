# Sources and portable changes

English | [中文](SOURCES.zh.md)

## Exact upstream source

Primary source: `.agents/skills/dsh-code-review/SKILL.md`, commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`, lines 8–49.

Supporting sources:

- `packages/AGENTS.md` lines 9–18;
- root `AGENTS.md` lines 116 and 122;
- `docs/defensive-patterns.md` lines 7–33;
- `docs/testing.md` lines 21–49;
- `docs/cookbook/responding-to-pr-review-on-a-stack.md` lines 9–24;
- `docs/cookbook/maintaining-dsh-code-review.md` lines 9–17, 19–48.

## Preserved wording

The opening limitation, review priorities, interface/lifecycle/consumer/enforcement/derived-state/bounds/real-entry/test-strength/transcript checks, and findings format closely retain the upstream wording.

## Portable changes

- Removed DeepSeek commands, package forms, invariant companions, Agent Note lifecycle, bilingual policy, and GitHub-only reply mechanics.
- Added explicit working-tree scope because the portable Skill covers more than PRs.
- Folded the upstream stacked-review rule “fix the introducing layer” into review receipt without importing stack mutation.
- Preserved human judgment from the maintenance cookbook: generated or delegated review output is not authority and one incident does not automatically become a universal rule.
- Made obsolete-test, dead-code coverage, and typed-boundary test review explicit from the upstream standing instructions.
- Added a Simplified Chinese translation without changing severity or proof requirements.

Pristine source: `../../../upstream/repository/.agents/skills/dsh-code-review/SKILL.md.orig`.
