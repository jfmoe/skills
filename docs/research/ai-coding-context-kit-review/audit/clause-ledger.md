# Portable clause ledger

English | [中文](clause-ledger.zh.md)

| Topic | Exact upstream source | Portable placement |
|---|---|---|
| Explore before planning; remain read-only; resolve discoverable facts; produce decision-complete plans | `apps/cli/config/agent-presets/standard/agent.cordis.yml` lines 113–124 | `plan-code-changes`; user instructions |
| Prefer a few proven simplifications; require current consumers; distinguish production, test/doc, and ambiguous use; assess net deletion for dependencies | `.agents/skills/dsh-find-simplifications/SKILL.md` lines 8–31, 47–80 | `audit-code-simplifications` |
| Require current owners and needs; require evidence for public choices; keep behavior with its owner | `packages/AGENTS.md` lines 10–12 | User and project instructions; simplification and review Skills |
| Review exact base/head and surrounding code; prioritize correctness, lifecycle, security, and required behavior | `.agents/skills/dsh-code-review/SKILL.md` lines 8–18 | `review-code-changes` |
| Review interfaces on both sides; trace lifecycle, consumers, enforcement, derived state, complete bounds, real entry paths, test strength, and transcript changes | `.agents/skills/dsh-code-review/SKILL.md` lines 20–49 | `review-code-changes` |
| Verify each review claim on technical grounds; fixes belong at the introducing layer; delegated reports are not proof | `.agents/skills/dsh-code-review/SKILL.md` line 49; `docs/cookbook/responding-to-pr-review-on-a-stack.md` lines 9–24 | Review Skill and project instructions |
| Run the narrowest evidence that would fail on the regression; CI owns exhaustive coverage and the platform matrix | `AGENTS.md` lines 87–93; `.agents/skills/dsh-pre-push-checks/SKILL.md` lines 27–64 | `select-relevant-checks`; user and project instructions |
| Coverage proves execution, not shipped correctness; uncovered code may be dead | `docs/testing.md` lines 9–13 | Test subtree instructions; check-selection Skill |
| Tests describe behavior rather than establishing correctness; change obsolete behavior with its tests | Root `AGENTS.md` line 122 | Project and test subtree instructions; simplification, review, and check-selection Skills |
| Trust typed same-process interfaces; place hostile-input validation and tests at actual untrusted boundaries | Root `AGENTS.md` line 116 | Project and test subtree instructions; simplification, review, and check-selection Skills |
| Mock only expensive or nondeterministic boundaries; verify external state; test the real entry path | `docs/testing.md` lines 21–35; `examples/AGENTS.md` lines 7–14 | Test subtree instructions; review and check-selection Skills |
| A guard must fail on the intended regression | `docs/testing.md` line 34; `docs/cookbook/responding-to-pr-review-on-a-stack.md` line 22 | Test subtree instructions; review Skill |
| Test resources own cleanup even on failure, retry, and timeout | `docs/testing.md` lines 27–29 | Test subtree instructions |
| One fact has one home; document current state; generated material changes owner-first | `docs/AGENTS.md` lines 7–17, 34–45, 59–75 | `apply-documentation-standards`; documentation subtree |
| Documentation format, word budgets, physical wrapping, and bilingual structure | `docs/AGENTS.md` lines 36–57; `docs/i18n/*` | Excluded from the portable documentation Skill by explicit user requirement; used only to produce this review bundle's Chinese counterparts. |
| Preserve every proposition: actor, condition, timing, modality, exception, ownership, side effect, failure, and consequence | `.agents/skills/dsh-prose-standard/SKILL.md` lines 28–42 | `review-code-prose` |
| Required prose depends on location; prompts and visible strings are behavior | `.agents/skills/dsh-prose-standard/SKILL.md` lines 44–61 | Prose Skill; agent-product subtree |
| CoT leakage one-test, eight-category taxonomy, explicit keep rules, and owner-first workflow | `.agents/skills/dsh-trim-cot-leakage/SKILL.md` lines 8–45, plus both references | Independent `trim-cot-leakage` Skill |
| Model-facing contracts use model task concepts, stable text is pinned, and dynamic behavior gets snapshot/e2e coverage | `packages/AGENTS.md` line 13; `AGENTS.md` lines 108, 124–127 | Agent-product subtree; review and test Skills |
| Enforce a decision in the operation that makes it; publish state after the commit point; bound the complete result | `packages/AGENTS.md` lines 14–16 | Project and agent-product instructions; review Skill |
| Fail closed when enforcement is unavailable; only explicit approval grants the action | `native/landlock-run/AGENTS.md` lines 9–16; `docs/subsystems/approval.md` lines 21–33, 84–88 | Security subtree |
| Scrub secrets from child environments; use private random exclusive temporary paths; unlink link-shaped paths | `docs/defensive-patterns.md` lines 27–33 | Security subtree |
| Async state is not synchronous state; disposal reaches quiescence; callback failures stay contained | `docs/defensive-patterns.md` lines 7–25 | Async subtree |
| Experimental status does not relax engineering, security, documentation, lifecycle, testing, invariant, or snapshot requirements | `packages/experimental/AGENTS.md` lines 5–9 | Project instructions |
| Hooks remain narrow; contributors run relevant checks once; CI owns exhaustive gates | `docs/development.md` lines 109–123 | Candidate hook/CI split |
| Review-guidance updates require source feedback, landed evidence, independent classification, human judgment, and resistance to one-incident overgeneralization | `docs/cookbook/maintaining-dsh-code-review.md` lines 9–17, 19–48 | Review Skill source record and maintenance note in project instructions |
