# Sources and portable changes

English | [中文](SOURCES.zh.md)

## Exact upstream source

Primary source: `.agents/skills/dsh-find-simplifications/SKILL.md`, commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`.

Retained ranges:

- lines 8–31: purpose and strong-candidate taxonomy;
- lines 33–63: broad survey, trust/lifecycle analysis, and dependency substitutions;
- lines 64–80: consumer proof and rejection bar;
- lines 99–121: durable proposal and inline-note distinction, adapted into reporting;
- lines 133–146: validation and reporting principles.

Supporting sources: root `AGENTS.md` lines 116 and 122; `packages/AGENTS.md` lines 9–12; `docs/testing.md` line 10; and `docs/defensive-patterns.md` lines 7–33.

## Portable changes

- Removed DeepSeek package names, protected twin backends, Agent Note paths, branch folding, PR mutation, and fixed commands.
- Kept the upstream candidate taxonomy and proof method substantially verbatim.
- Converted the DeepSeek Agent Note output into a repository-neutral evidence report; a target project may route durable candidates into its own decision-record format.
- Made the upstream obsolete-behavior, dead-code coverage, and typed-boundary test rules explicit in the candidate and tied them to consumer evidence.
- Added license, security, and platform support to dependency health because they are boundary facts required outside the original monorepo.
- Added a Simplified Chinese translation without changing the decision bar.

Pristine source: `../../../upstream/repository/.agents/skills/dsh-find-simplifications/SKILL.md.orig`.
