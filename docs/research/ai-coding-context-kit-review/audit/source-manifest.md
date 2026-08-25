# Source manifest

English | [中文](source-manifest.zh.md)

The canonical inventory is `source-manifest.tsv`. It contains 70 unique upstream files from commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`.

The inventory includes:

- 20 `AGENTS.md` files: 16 active instruction files and four test fixtures.
- Five active `CLAUDE.md` symlinks. Each link blob contains `AGENTS.md` and resolves to the adjacent instruction file, so the entrypoints contribute no additional clause.
- One active `.claude/skills` symlink whose link blob is `../.agents/skills`; it exposes the same 11 repository Skills and contributes no additional Skill text.
- 11 repository Skills with every wrapper, reference, and script in their directories.
- Four shipped Agent compositions, four display-metadata files, and two preset-local Skills.
- Twelve directly relevant development, testing, review, approval, Agent Note, and translation policy files.
- The upstream MIT license.

Each row records the original path, safe mirror path, Git blob SHA, line count, source kind, and one disposition. The verifier rejects duplicate paths, duplicate mirror paths, missing mirrors, hash mismatches, unknown dispositions, and discovery-sensitive mirror names.

`prompt-surface-scan.tsv` is the broader discovery boundary. It records 125 path-based candidates matching recognized agent-instruction and Skill-discovery entrypoints, `SKILL.md`, prompt/instruction names, or the shipped preset tree. Paths outside the 70-file corpus are explicitly classified as product runtime, tooling implementation, test/fixture, historical note, or other non-portable context.
