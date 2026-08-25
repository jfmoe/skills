# Sources and portable changes

English | [中文](SOURCES.zh.md)

## Exact upstream source

Primary sources at commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`:

- `.agents/skills/dsh-doc-standards/SKILL.md` lines 8–56;
- `docs/AGENTS.md` lines 7–45 and 59–75;
- `.agents/skills/dsh-doc-site-sync/SKILL.md` lines 8–27 and 43–54;
- `.agents/notes/implemented/AGENTS.md` lines 5–13.

## Preserved wording

The upstream authoring order, tutorial/reference distinction, “one home per fact,” current-state rule, owner-first generated material, slop categories, and semantic-review boundary are retained closely.

## Portable changes

- Removed all Markdown wrapping, word-budget, heading, bilingual pairing, locale, VitePress, DeepSeek document-tier names, Agent Note format, and fixed command requirements.
- Replaced the fixed tier table with semantic roles that a target repository maps to its own hierarchy.
- Added the explicit no-formatting boundary from the user's requirement.
- Kept `dsh-trim-cot-leakage` independent as `trim-cot-leakage`; this Skill links to it rather than absorbing its taxonomy.
- Added a Simplified Chinese translation without adding a formatting policy.

Pristine source: `../../../upstream/repository/.agents/skills/dsh-doc-standards/SKILL.md.orig`.
