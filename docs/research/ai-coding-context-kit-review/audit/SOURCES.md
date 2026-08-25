# Sources for audit artifacts

English | [中文](SOURCES.zh.md)

| Artifact | Source |
|---|---|
| `source-manifest.tsv` | Git tree and blob objects at upstream commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`; corpus boundary defined in the approved rebuild plan. |
| `prompt-surface-scan.tsv` | Path scan over the same Git tree for recognized agent-instruction basenames (including `AGENTS.md` and `CLAUDE.md`), Skill-discovery symlinks, every `SKILL.md`, every prompt/instruction-named file, and every shipped preset path. |
| `source-manifest*.md` | The two TSV inventories and their computed counts. |
| `disposition-ledger*.md` | Every active `AGENTS.md` and `CLAUDE.md`, every repository and preset-local Skill, all shipped presets, and the supplemental policies in the manifest. |
| `clause-ledger*.md` | Exact line ranges named in each table row; no line range is inferred from a derived artifact. |
| `scripts/verify-review-bundle.mjs` and its Chinese explanation | Integrity requirements in the approved rebuild plan; Git tree and blob formats; local Skill discovery constraints from `skills/manage-skills/SKILL.md`; expanded instruction/Skill/preset discovery rule proven against the pinned tree. |
| `scripts/smoke-agent-guardrails.mjs` and its Chinese explanation | Behavioral seams of the candidate project verifier: exact staged snapshots, rename coverage, paired projections, protected paths, and base-to-HEAD mode. |
| `validation-report*.md` | Actual command results produced after rebuilding. |

The TSV files are language-neutral structured evidence. Their English and Chinese explanatory documents are the human-readable counterparts.
