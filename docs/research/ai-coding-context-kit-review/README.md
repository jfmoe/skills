# AI Coding Context Kit — Review Bundle

English | [中文](README.zh.md)

This directory is a from-scratch, inactive review bundle derived from `deepseek-ai/deepseek-harness` at commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`.

The bundle is evidence-first. A machine-readable manifest accounts for 70 mirrored source files: 20 `AGENTS.md` files, five active `CLAUDE.md` symlinks that resolve to their adjacent `AGENTS.md` files, one `.claude/skills` symlink exposing the same 11 repository Skills, the 11 Skill directories and their support files, four shipped Agent presets, two preset-local Skills, directly referenced development and translation policies, and the MIT license. A broader 125-path prompt-surface scan records recognized agent-instruction and Skill-discovery entrypoints, product runtime prompts, fixtures, snapshots, and historical notes that were inspected as possible scope but excluded from portable coding context.

Nothing here is installed or active. Candidate entrypoints use `SKILL.md.review` and `AGENTS.md.review`; UI metadata uses `openai.yaml.review`. The pristine mirror renames discovery-sensitive source filenames to `.orig` while preserving their bytes.

## Layout

- `audit/`: source manifest, prompt-surface scan, disposition ledger, clause ledger, verifier, and validation report.
- `upstream/`: byte-identical evidence copied from the pinned commit.
- `artifacts/user/`: candidate user-level standing instructions.
- `artifacts/project/`: candidate project and subtree instructions, hook, CI workflow, configuration, and verifier.
- `artifacts/skills/`: seven independent candidate Skills.
- `artifacts/registry/upstream/`: proposed fork snapshots and metadata for later promotion.

## Translation contract

Every derived artifact has a Simplified Chinese counterpart. Markdown prompt artifacts use a sibling `.zh.md` form; executable or structured artifacts use one canonical implementation plus a sibling `.zh.md` explanation so two executable copies cannot drift. Each artifact unit also has English and Chinese source records listing the exact upstream files and line ranges.

The byte-identical `upstream/` mirror is evidence, not a derived artifact. It is intentionally not translated: changing its text would destroy the hash proof. Its bilingual README explains that boundary.

## Candidate Skills

| Skill | Purpose |
|---|---|
| `plan-code-changes` | Read-only exploration and decision-complete implementation planning. |
| `audit-code-simplifications` | Evidence-backed removal, folding, demotion, and dependency substitution. |
| `review-code-changes` | Semantic review of a branch, PR, commit range, or working-tree diff. |
| `select-relevant-checks` | Select the narrowest credible tests and checks for the changed surface. |
| `apply-documentation-standards` | Place and review documentation by meaning and ownership, without formatting policy. |
| `review-code-prose` | Preserve complete contracts while trimming repetition, narration, and decoration. |
| `trim-cot-leakage` | Independently detect and repair reasoning-transcript leakage, with its full taxonomy, examples, and recall batteries. |

Independent upstream Skills remain independent. In particular, `dsh-trim-cot-leakage` is not absorbed into `review-code-prose`; the two Skills only cross-reference one another.

## Review order

1. Read `audit/source-manifest.md` and `audit/prompt-surface-scan.tsv`.
2. Review `audit/disposition-ledger.md` and `audit/clause-ledger.md`.
3. Compare each artifact with its `SOURCES.md` and the pinned mirror.
4. Review English and Chinese counterparts together.
5. Run `node audit/scripts/verify-review-bundle.mjs`; when a local upstream clone is available, also pass `--upstream <clone>` to rederive the full discovery set from the pinned Git tree.
6. Read `audit/validation-report.md` before approving promotion.

Promotion, installation, registry regeneration, and copying instructions into a real user or project context require a separate explicit request.
