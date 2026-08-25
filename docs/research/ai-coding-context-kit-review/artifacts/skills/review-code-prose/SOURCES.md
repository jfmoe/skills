# Sources and portable changes

English | [中文](SOURCES.zh.md)

## Exact upstream source

Primary source: `.agents/skills/dsh-prose-standard/SKILL.md`, commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`, lines 8–81.

Supporting sources:

- `docs/AGENTS.md` lines 36–45 and 59–75;
- root `AGENTS.md` lines 137–143;
- `examples/AGENTS.md` lines 16–18;
- upstream examples at `.agents/skills/dsh-prose-standard/references/examples.md`, lines 1–167.

## Preserved wording

The complete-proposition rule, local-contract rule, required coverage by prose location, workflow classifications, and borderline-case definition substantially retain the upstream wording. The English examples are copied verbatim.

## Portable changes

- Removed the unconditional DeepSeek `vendor/` and archived-note exclusions; the portable Skill follows the target repository's protected-path rules.
- Removed DeepSeek bilingual pairing, Agent Note format, package README template, fixed commands, PR-channel mechanics, and learned-rule mutation of the reference file.
- Replaced the original hard stop on a missing `scope` with a safe boundary derived from named files, the current diff, or explicit paths.
- Kept `trim-cot-leakage` independent and linked it instead of reducing its taxonomy to a prose subsection.
- Added Simplified Chinese translations of the Skill and examples without adding propositions.

Pristine source: `../../../upstream/repository/.agents/skills/dsh-prose-standard/SKILL.md.orig`; examples: the adjacent mirrored `references/examples.md`.
