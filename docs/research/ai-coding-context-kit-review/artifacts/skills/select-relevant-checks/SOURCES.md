# Sources and portable changes

English | [中文](SOURCES.zh.md)

## Exact upstream source

Primary source: `.agents/skills/dsh-pre-push-checks/SKILL.md`, commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`.

Retained ranges:

- lines 8–37: hook/CI division, scope inspection, and relevant evidence;
- lines 39–60: focused test and coverage selection;
- lines 62–64: full rehearsal boundary;
- lines 83–92: failure handling.

Supporting sources:

- root `AGENTS.md` lines 87–93, 116, and 122;
- `docs/testing.md` lines 7–49;
- `examples/AGENTS.md` lines 7–18;
- `packages/client/AGENTS.md` lines 113–130 for the narrow check ladder.

## Portable changes

- Removed DeepSeek commands, exact coverage thresholds, GitHub stack sync, force-push, push procedure, and remote-check inspection.
- Made commit, push, and remote mutation explicitly outside the Skill's authorization.
- Preserved the upstream “narrowest evidence,” “do not repeat passing checks,” coverage-scope, full-rehearsal, and environment-proof rules.
- Preserved the distinction between a regression and an obsolete test, the dead-code interpretation of uncovered branches, and the typed-boundary limit on hostile-input tests.
- Added UI-path verification from the upstream GUI instructions.
- Added a Simplified Chinese translation without changing validation strength.

Pristine source: `../../../upstream/repository/.agents/skills/dsh-pre-push-checks/SKILL.md.orig`; wrapper: the adjacent mirrored `agents/openai.yaml`.
