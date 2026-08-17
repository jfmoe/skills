# AI Coding Context Kit — Review Bundle

A self-contained review copy of portable AI-coding instructions and workflows extracted from DeepSeek Harness at commit `47f943859bef60e4160492346772ded9b24f765a`.

## Review status

Nothing in this folder is installed, registered, or active repository policy. Candidate Skill and scoped-instruction entry files are named `SKILL.md.review` and `AGENTS.md.review`, so recursive discovery ignores them. Proposed fork metadata and pristine snapshots live under this folder's `registry/upstream/`; the live generated `registry/ledger.yaml` intentionally contains no entries for these candidates.

Review and approve this folder as one unit before promoting any artifact into its runtime location.

## Layout

- `user/`: disabled candidate user-level defaults and their source record.
- `project/`: disabled candidate project/subtree AGENTS files, hook, CI, config, verifier, and adjacent source records.
- `skills/`: five candidate Skills, disabled for discovery by the `.review` suffix.
- `registry/upstream/`: proposed pristine fork snapshots and metadata.
- `SOURCE_CATALOG.md`: complete inspected-source inventory and include/adapt/exclude decisions.

## Suggested review order

1. Read `SOURCE_CATALOG.md` to audit source coverage and exclusions.
2. Review `user/` and `project/` for always-on versus scoped prompt placement.
3. Review each disabled candidate under `skills/` together with its `references/upstream-sources.md`.
4. Review `project/scripts/`, `.githooks/`, `.github/`, and the config as one mechanical unit.
5. Compare fork candidates with their exact pristine copies under `registry/upstream/`.

The kit separates concerns by enforcement strength:

- `user/AGENTS.md.review`: stable cross-project working preferences proposed for a future user instruction file.
- `project/AGENTS.md.review`: always-on repository invariants proposed for a target repository.
- `project/subtrees/*/AGENTS.md.review`: optional rules proposed only for relevant code.
- `project/.githooks/`, `project/.github/`, and `project/scripts/`: mechanical checks only.
- Candidate workflow skills remain flat under this bundle's `skills/`; promotion moves each complete directory to the repository's top-level `skills/` tree.

## Candidate skills

| Skill | Use |
|---|---|
| [`plan-code-changes`](skills/plan-code-changes/SKILL.md.review) | Read-only repository exploration and decision-complete plans. |
| [`audit-code-simplifications`](skills/audit-code-simplifications/SKILL.md.review) | Evidence-backed removal, folding, demotion, and dependency replacement. |
| [`review-code-changes`](skills/review-code-changes/SKILL.md.review) | Semantic review of a branch, PR, commit range, or working-tree diff. |
| [`select-relevant-checks`](skills/select-relevant-checks/SKILL.md.review) | Diff-driven selection of the narrowest credible tests and checks. |
| [`review-code-prose`](skills/review-code-prose/SKILL.md.review) | Contract-preserving review of docs, comments, prompts, diagnostics, and visible strings. |

Each candidate contains `references/upstream-sources.md` covering its future `SKILL.md`, wrapper, bundled references, commit-pinned source locations, verbatim/adapted status, portable changes, and the upstream MIT notice.

[`SOURCE_CATALOG.md`](SOURCE_CATALOG.md) records every non-fixture `AGENTS.md`, repository Skill, and shipped Agent preset inspected at the pinned commit, including material intentionally excluded from the portable kit.

## Promotion after approval

1. Move each approved `skills/<name>/` directory to the repository's top-level `skills/<name>/` and rename `SKILL.md.review` to `SKILL.md`.
2. Move each approved fork snapshot from this bundle's `registry/upstream/<name>/` to the live `registry/upstream/<name>/`.
3. Regenerate the live ledger from the promoted `meta.yaml` files; never copy or hand-edit a ledger fragment.
4. Copy or merge `user/AGENTS.md.review` only into an explicitly chosen user-global `AGENTS.md` or equivalent instruction file.
5. Make a promotion copy of `project/`, rename every `AGENTS.md.review` in that copy to `AGENTS.md`, then adapt the root and subtree rules to the target repository. Keep only durable facts and remove pointers to Skills not promoted.
6. Copy the script, config, hook, and CI workflow together; configure protected paths and source/projection relationships before relying on them.
7. Install approved Skills only after a separate installation request.

## Mechanical guardrails

After approval, make the promotion copy described above, copy its contents into a target repository root, merge rather than overwrite an existing `AGENTS.md`, and adapt `agent-guardrails.config.json`. Enable the versioned hook explicitly:

```sh
git config core.hooksPath .githooks
```

The hook runs staged `git diff --check` plus the shared verifier against the exact index snapshot. The pull-request workflow runs the same verifier against the exact base SHA and resulting `HEAD` snapshot. Empty protected-path and source/projection arrays are intentional; populate them only from facts that are true in the target repository.

Do not copy all material blindly. Security policy, architecture, commands, paths, coverage thresholds, snapshot mandates, compatibility stance, and generated-file ownership remain project facts.

## Provenance

This collection is derived from `deepseek-ai/deepseek-harness`, primarily its root and subtree `AGENTS.md` files, `.agents/skills/`, `docs/testing.md`, `docs/defensive-patterns.md`, and standard Agent preset. Every deliverable is covered by a source record: AGENTS, hook, CI, config, and script artifacts use adjacent `.sources.md` files; each Skill uses `references/upstream-sources.md`; this index and the catalog have their own sidecars. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for licensing.
