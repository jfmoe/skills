# Disposition ledger

English | [中文](disposition-ledger.zh.md)

This ledger explains every source family. The row-level decision remains authoritative in `source-manifest.tsv`.

## AGENTS instructions

| Source | Disposition |
|---|---|
| Root `AGENTS.md`; `docs/AGENTS.md`; `packages/AGENTS.md`; `examples/AGENTS.md` | Adapt general planning, ownership, documentation, model-facing, and testing rules. Remove repository layout, exact commands, package names, formatting, and bilingual policy. |
| `.agents/notes/{,implemented,archived}/AGENTS.md` | Adapt current-authority, decision-record, and frozen-history rules. Do not copy the DeepSeek triplet lifecycle as a universal default. |
| Root, `examples/`, `packages/`, `.agents/notes/implemented/`, and `vendor/` `CLAUDE.md` | Retain each symlink blob as active entrypoint evidence. Every link resolves to the adjacent `AGENTS.md`, so it adds no new portable clause and is classified explicitly rather than silently omitted. |
| `native/landlock-run/AGENTS.md`; `packages/web/AGENTS.md` | Adapt fail-closed execution, safe paths, and credential-bearing redirect rules into the security subtree. |
| `packages/experimental/AGENTS.md` | Adapt the rule that experimental status does not relax engineering, security, documentation, lifecycle, or testing obligations. |
| `vendor/AGENTS.md`; `website/AGENTS.md` | Adapt protected-source and canonical-source/generated-projection rules into project instructions and mechanical guardrails. |
| `.github/AGENTS.md`; `packages/client/AGENTS.md`; `packages/schedule/AGENTS.md`; `scripts/AGENTS.md` | Keep as reviewed project-specific references. Generic testing and lifecycle propositions are already sourced from their owning general documents. |
| Four snapshot `AGENTS.md` files | Exclude as test data, while retaining exact mirrors and explicit manifest rows. |

## Skills

| Upstream Skill | Disposition |
|---|---|
| `.claude/skills` | Retain the symlink blob as the Claude discovery entrypoint for `.agents/skills`; it exposes the same 11 repository Skills and does not create a twelfth Skill. |
| `dsh-code-review` | Independent fork: `review-code-changes`. |
| `dsh-doc-standards` | Independent fork: `apply-documentation-standards`; formatting, budgets, and bilingual layout are removed by user requirement. |
| `dsh-find-simplifications` | Independent fork: `audit-code-simplifications`. |
| `dsh-pre-push-checks` | Independent fork: `select-relevant-checks`; push and stack mutation mechanics are excluded. |
| `dsh-prose-standard` | Independent fork: `review-code-prose`, including its examples. |
| `dsh-trim-cot-leakage` | Independent fork: `trim-cot-leakage`, including the complete taxonomy, exceptions, workflow, examples, and recall batteries. It is not merged into the prose Skill. |
| `dsh-archive-agent-notes` | Reference only. Its future-value test informs decision-record guidance, but its exact lifecycle and sealed triplets are project policy. |
| `dsh-doc-site-sync` | Adapt canonical-source/projection mechanics into project guardrails; VitePress and bilingual routing remain project-specific. |
| `dsh-merging-stacked-prs` | Exclude from portable defaults because it mutates remote stack state and depends on repository policy and GitHub stack support. |
| `dsh-translate-docs` | Translation reference for this bilingual review bundle; no general Skill candidate. |
| `record-browser-gif` | Exclude its mandatory-GIF and assets-branch workflow. Retain actual UI-path verification as a testing principle. |
| Two Cordis preset-local Skills | Exclude as product-specific runtime authoring workflows; retain the general “inspect the real interface before writing” principle in project guidance. |

## Presets and supplemental policies

The plan-mode text in the standard preset is forked into `plan-code-changes`; duplicate copies in code and Cordis presets are recorded as references. Minimal-shell guidance and Cordis self-modification persona remain product runtime. Testing, defensive patterns, development hooks, review maintenance, review response, approval, Agent Note, and translation policies contribute the exact clauses listed in `clause-ledger.md`.
