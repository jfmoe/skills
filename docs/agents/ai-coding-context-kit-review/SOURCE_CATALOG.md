# DeepSeek Harness agent-prompt source catalog

This catalog accounts for the AI-coding instruction surfaces inspected in `deepseek-ai/deepseek-harness` at commit `47f943859bef60e4160492346772ded9b24f765a`. It distinguishes portable prompt material from repository-specific runtime, process, formatting, and product rules.

## Audit boundary

The fixed tree contains:

- 15 active, non-fixture `AGENTS.md` files;
- 4 additional `AGENTS.md` test fixtures, treated as sample data rather than applicable instructions;
- 11 repository Skills and 6 owning `agents/openai.yaml` wrappers;
- 4 shipped Agent preset compositions with model-facing persona, plan-mode, or tool-description text.

`Retained` means wording was carried into a portable artifact. `Adapted` means product names, paths, commands, or repository-only policy were removed. `Excluded` means the material was read but has no unique portable AI-coding rule, or would be unsafe or misleading as a general default.

## Active AGENTS files

| Source and exact range | Disposition | Portable destination or exclusion reason |
|---|---|---|
| [`.agents/notes/AGENTS.md`, lines 1-7](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/notes/AGENTS.md#L1-L7) | Adapted | Durable rationale and current-authority principles inform `review-code-prose`; exact Agent Note triplet and supersession workflow is repository-specific. |
| [`.agents/notes/archived/AGENTS.md`, lines 1-7](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/notes/archived/AGENTS.md#L1-L7) | Retained | Frozen-content exclusion and protected-path policy in `project/AGENTS.md`, the prose Skill, config, and verifier. |
| [`.agents/notes/implemented/AGENTS.md`, lines 1-13](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/notes/implemented/AGENTS.md#L1-L13) | Adapted | Current-state documentation and shipped-decision maintenance in `project/AGENTS.md` and `review-code-prose`. |
| [`.github/AGENTS.md`, lines 1-3](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.github/AGENTS.md#L1-L3) | Excluded | DeepSeek's Windows runner and failover topology is a project CI fact. |
| [`AGENTS.md`, lines 1-149](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/AGENTS.md#L1-L149) | Retained and adapted | Cross-project defaults, project invariants, testing policy, documentation semantics, hook separation, and source maps throughout the kit. |
| [`docs/AGENTS.md`, lines 1-75](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/AGENTS.md#L1-L75) | Adapted | Semantic placement, one owner per fact, current-state prose, and reasoning-transcript rules. Formatting, word budgets, exact tiers, and bilingual rules are excluded. |
| [`examples/AGENTS.md`, lines 1-20](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/examples/AGENTS.md#L1-L20) | Adapted | Real-entry smoke tests, external-state verification, and non-narrative configuration comments in `project/AGENTS.md`, `select-relevant-checks`, and `review-code-prose`. |
| [`native/landlock-run/AGENTS.md`, lines 1-50](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/native/landlock-run/AGENTS.md#L1-L50) | Adapted | Fail-closed confinement and safe path handling in `subtrees/security-sensitive/AGENTS.md`; Landlock build commands are excluded. |
| [`packages/AGENTS.md`, lines 1-27](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/AGENTS.md#L1-L27) | Retained and adapted | Ownership, consumer evidence, lifecycle, enforcement, model perspective, and complete-result bounds across project instructions and Skills. |
| [`packages/client/AGENTS.md`, lines 1-107](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/client/AGENTS.md#L1-L107) | Excluded after review | Slot, store, React, export, and package graph rules encode DeepSeek's settled GUI architecture. Its generic user-visible testing principles are already owned by root policy and `docs/testing.md`. |
| [`packages/schedule/AGENTS.md`, lines 1-10](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/schedule/AGENTS.md#L1-L10) | Excluded after review | The schedule event stream, fork seed, flush barriers, and maintenance phase are domain contracts; generic lifecycle rules are independently sourced from `docs/defensive-patterns.md`. |
| [`packages/web/AGENTS.md`, lines 1-5](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/web/AGENTS.md#L1-L5) | Adapted | Credential-bearing redirect denial in `subtrees/security-sensitive/AGENTS.md`. |
| [`scripts/AGENTS.md`, lines 1-3](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/scripts/AGENTS.md#L1-L3) | Excluded | Pnpm invocation and repository glob normalization are implementation-specific script conventions. |
| [`vendor/AGENTS.md`, lines 1-7](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/vendor/AGENTS.md#L1-L7) | Adapted | Explicit protected-path policy in config and verifier; DeepSeek's vendor update command is excluded. |
| [`website/AGENTS.md`, lines 1-13](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/website/AGENTS.md#L1-L13) | Adapted | Canonical-source/generated-projection policy in `project/AGENTS.md`, config, and verifier. |

## Repository Skills

| Source and exact range | Disposition | Portable destination or exclusion reason |
|---|---|---|
| [`dsh-archive-agent-notes`, lines 1-68](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-archive-agent-notes/SKILL.md#L1-L68) | Excluded | DeepSeek Agent Note lifecycle, triplets, manifests, and archive commands are project-specific. Future-value judgment is represented generically in the prose Skill. |
| [`dsh-code-review`, lines 1-49](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-code-review/SKILL.md#L1-L49) | Forked | `skills/review-code-changes`; exact upstream `SKILL.md.orig` retained under `registry/upstream/`. |
| [`dsh-doc-site-sync`, lines 1-86](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-doc-site-sync/SKILL.md#L1-L86) | Adapted | Canonical-source/projection policy in config and verifier; VitePress routes, bilingual layout, and DeepSeek commands are excluded. |
| [`dsh-doc-standards`, lines 1-56](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-doc-standards/SKILL.md#L1-L56) | Adapted | Semantic ownership and current-state documentation in `review-code-prose`; formatting, budgets, hierarchy names, and bilingual gates are excluded as requested. |
| [`dsh-find-simplifications`, lines 1-146](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-find-simplifications/SKILL.md#L1-L146) | Forked | `skills/audit-code-simplifications`; exact upstream `SKILL.md.orig` retained. |
| [`dsh-merging-stacked-prs`, lines 1-127](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-merging-stacked-prs/SKILL.md#L1-L127) | Excluded | Mutating GitHub-stack workflow, extension assumptions, merge policy, and repository history rules are not universal AI-coding context. |
| [`dsh-pre-push-checks`, lines 1-115](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-pre-push-checks/SKILL.md#L1-L115) | Forked | `skills/select-relevant-checks`; exact upstream Skill and wrapper retained. Stack rewriting and push mechanics are excluded. |
| [`dsh-prose-standard`, lines 1-81](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-prose-standard/SKILL.md#L1-L81) | Forked | `skills/review-code-prose`; exact upstream Skill, wrapper, and examples retained, with portable semantic rules in the candidate fork. |
| [`dsh-translate-docs`, lines 1-74](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-translate-docs/SKILL.md#L1-L74) | Excluded | Manual bilingual pairing, terminology, and repository translation workflow are intentionally outside the requested universal documentation rules. |
| [`dsh-trim-cot-leakage`, lines 1-45](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-trim-cot-leakage/SKILL.md#L1-L45) | Adapted | Contract-preserving deletion of reasoning transcripts is integrated into `review-code-prose`; DeepSeek recall batteries and bilingual handling are excluded. |
| [`record-browser-gif`, lines 1-110](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/record-browser-gif/SKILL.md#L1-L110) | Excluded | Recording, credential, assets-branch, and mandatory PR-GIF workflow is product/process-specific; the portable test Skill keeps actual UI-path verification without mandating media. |

## Skill wrappers

The wrappers contain invocation text rather than additional workflow rules. They were read with their owning Skills.

| Source and exact range | Disposition |
|---|---|
| [`dsh-archive-agent-notes/agents/openai.yaml`, lines 1-4](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-archive-agent-notes/agents/openai.yaml#L1-L4) | Excluded with the owning Skill. |
| [`dsh-doc-site-sync/agents/openai.yaml`, lines 1-4](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-doc-site-sync/agents/openai.yaml#L1-L4) | Excluded with the owning DeepSeek workflow. |
| [`dsh-pre-push-checks/agents/openai.yaml`, lines 1-4](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-pre-push-checks/agents/openai.yaml#L1-L4) | Preserved in the pristine snapshot; adapted thin wrapper ships with `select-relevant-checks`. |
| [`dsh-prose-standard/agents/openai.yaml`, lines 1-4](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-prose-standard/agents/openai.yaml#L1-L4) | Preserved in the pristine snapshot; adapted thin wrapper ships with `review-code-prose`. |
| [`dsh-translate-docs/agents/openai.yaml`, lines 1-7](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-translate-docs/agents/openai.yaml#L1-L7) | Excluded with the owning manual translation workflow. |
| [`record-browser-gif/agents/openai.yaml`, lines 1-4](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/record-browser-gif/agents/openai.yaml#L1-L4) | Excluded with the owning recording workflow. |

## Shipped Agent presets

| Source and exact range | Disposition | Portable destination or exclusion reason |
|---|---|---|
| [`standard/agent.cordis.yml`, lines 22-33 and 100-124](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/apps/cli/config/agent-presets/standard/agent.cordis.yml#L22-L124) | Forked from prompt source | Plan-mode prompt becomes `plan-code-changes` and user defaults; the complete pristine preset file is retained under `registry/upstream/plan-code-changes/`. Identity, registry, tool, and runtime composition are platform internals. |
| [`code/agent.cordis.yml`, lines 29-40 and 107-131](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/apps/cli/config/agent-presets/code/agent.cordis.yml#L29-L131) | Duplicate prompt reviewed | Plan text duplicates `standard`; Code Mode presentation is runtime integration, not a portable instruction. |
| [`cordis/agent.cordis.yml`, lines 15-34 and 88-112](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/apps/cli/config/agent-presets/cordis/agent.cordis.yml#L15-L112) | Partly duplicate, otherwise excluded | Plan text duplicates `standard`; self-modifying Cordis persona and shipped-preset paths are product-specific trust and ownership rules. |
| [`minimal/agent.cordis.yml`, lines 1-13 and 36-44](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/apps/cli/config/agent-presets/minimal/agent.cordis.yml#L1-L44) | Excluded | Generic identity plus constraints of one persistent shell tool; its background-process guidance depends on that tool's runtime and is not a safe cross-agent default. |

## AGENTS test fixtures

These four files are expected-output inputs that test instruction discovery and nesting. They are not repository policy and contributed no portable requirement:

- [`examples/acp-agent/tests/snapshots/agent-instructions/workspace/AGENTS.md`, line 1](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/examples/acp-agent/tests/snapshots/agent-instructions/workspace/AGENTS.md#L1)
- [`examples/acp-agent/tests/snapshots/agent-instructions/workspace/nested/AGENTS.md`, line 1](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/examples/acp-agent/tests/snapshots/agent-instructions/workspace/nested/AGENTS.md#L1)
- [`examples/acp-agent/tests/snapshots/code-mode-workspace-context/workspace/AGENTS.md`, line 1](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/examples/acp-agent/tests/snapshots/code-mode-workspace-context/workspace/AGENTS.md#L1)
- [`examples/acp-agent/tests/snapshots/code-mode-workspace-context/workspace/nested/AGENTS.md`, line 1](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/examples/acp-agent/tests/snapshots/code-mode-workspace-context/workspace/nested/AGENTS.md#L1)

## Supplemental development policies

These are not prompt files, but applicable prompt surfaces point to them and their general rules were extracted:

- [`docs/testing.md`, lines 1-49](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/testing.md#L1-L49): evidence strength, external-state verification, real entry paths, resource ownership, and snapshots.
- [`docs/defensive-patterns.md`, lines 1-33](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/defensive-patterns.md#L1-L33): orthogonal outcomes, public normalization, async intervals, disposal, callbacks, temporary paths, and link-shaped deletion.
- [`docs/subsystems/approval.md`, lines 5-28 and 84-88](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/subsystems/approval.md#L5-L88): fail-closed authorization and enforcement at the owning operation.

## Placement result

- Stable cross-project behavior belongs in `user/AGENTS.md`.
- Durable repository facts belong in `project/AGENTS.md`.
- Conditional domain rules belong in the narrowest subtree `AGENTS.md`.
- Repeatable, judgment-heavy workflows belong in Skills.
- Objective existence, protected-path, projection, and diff-integrity rules belong in hook/CI code.
- Product runtime composition, exact commands, formatting policy, bilingual workflow, remote mutation, and repository-specific architecture stay out of the portable defaults unless a target project independently adopts them.
