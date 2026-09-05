---
name: trim-cot-leakage
description: Audit or fix prose that reads like a leaked reasoning transcript, including dead design-session citations, audit item codes, uncommitted draft sections, change narration, stack or review vantage, reviewer-addressed justification, control-flow narration, test walkthroughs, or hedged planning residue.
---

# Trimming Chain-of-Thought Leakage

Chain-of-thought leakage is prose whose vantage is the authoring session rather than the repository: it cites artifacts only that session could see, narrates the change instead of the state, or argues with a reviewer who has left. The fix is never deletion alone when a passage carries factual clauses—restate each so it stands at the current repository state, then delete the transcript around it. A passage carrying none, such as an audit code or control-flow narration, is deleted outright.

The complete-proposition rule: before deleting a passage, enumerate every proposition it carries; each proposition that still holds at the current repository state must survive the trim. This skill is guidance, not a script.

## The one test

For every suspect passage ask: **could a reader at the current repository state, with no access to any session transcript, review thread, or uncommitted draft, resolve every reference and verify every claim?** If no, restate the surviving facts from the repository's vantage and delete the rest. If yes, it is not leakage, however historical it sounds—but resolvability only clears this skill's bar: on current-state surfaces such as READMEs, docs, and JSDoc, a resolvable change story is still change narration, and class 3 routes it to its sanctioned home.

## Taxonomy

1. **Dead design-session citations** — `(decision 7)`, `(audit C2)`, `design §4.7`, `plan §1.4`, phase labels such as `T4`, `W3`, or `P-I`, “the design ledger,” and “(B ruling).” If the decision has a committed owner, cite it by name and path; otherwise delete the citation and restate its factual clause to stand alone.
2. **Stack and PR vantage** — “a later PR in this stack,” “this PR adds,” “the previous commit.” State the shipped mechanism or extension point; deferred work moves to an owned TODO marker or issue reference.
3. **Change narration and version stamps** — “used to,” “no longer,” “the old X,” and indexical stamps such as “v1,” “this cut,” “today,” or “now” contrasting with a past state. State the present behavior. A fixed regression becomes a present-tense counterfactual such as “without X, Y happens,” never repository history such as “used to Y.”
4. **Review choreography** — “Rejected in review,” “the reviewer confirmed,” draft ordinals such as “v5 of this note,” and round attributions. Keep the surviving decision and rationale as plain fact; delete who said it when.
5. **Reviewer-addressed justification** — “the cast is safe—it simply…,” “this is correct because….” A comment arguing its own correctness addresses a reviewer, not a maintainer. State the invariant that makes the code safe, or delete the comment if the code shows it.
6. **Restatement and derivation transcripts** — control-flow narration such as “first we X, then we Y,” test walkthroughs, and proofs of obvious branches. Delete them; keep only a non-obvious contract or invariant.
7. **Hedges and planning residue** — “probably fine for now,” “should be enough,” and deferrals with no owner. Promote to an owned TODO/FIXME or restate the actual bound; delete the hedge.
8. **Authoring-language slips** — untranslated working-language fragments or private draft separators in prose whose language is otherwise consistent. Translate or delete them.

## What is not leakage

Unaided citation passes fail in both directions by deleting durable references and keeping dead ones. Apply these keep rules as written; [examples](references/examples.md) calibrate each:

- **Issue references** — `#1470`, `TODO(name):`, and “issue #N owns the follow-up” resolve at the current repository state; keep them on any surface.
- **Merged-PR and issue citations inside decision records and incident records** — sanctioned evidence when those document types own change history.
- **Suppression justifications** — linter-disable reasons, coverage-ignore reasons, and empty-catch explanations are required prose; fix a false reason, never delete it.
- **Counterfactual-present regression pins** — “without X, Y happens,” “a naive X would….”
- **Measured bounds** — “measured: 512 nests ≈ 0.15s” calibrating a constant; the provenance word “measured” is load-bearing.
- **Runtime old/new states** — “the old connection drains before the new one accepts” describes runtime lifecycle, not repository history.
- **Historical stage names inside a record's change-story section** — “the first cut shipped X” may be safe there; indexical stamps such as “this cut” remain unsafe.
- **External references that resolve outside the repository by design** — standards sections and named design artifacts. The section-number concern covers uncommitted internal drafts, not resolvable external standards or committed documents.
- **Project voice and genre forms** — “we” as project voice and an “Alternatives considered” section are not leakage by themselves.

## Workflow

1. Establish explicit scope and applicable protected paths. Do not edit vendor or third-party source or frozen records. Recorded fixtures and snapshots are derivatives, not prose targets: change the owning source or scenario and regenerate them only when an authorized behavior change requires new evidence.
2. Audit read-only first. Run the [recall batteries](references/recall-batteries.md), calibrating each probe against a known positive and a near-miss negative before trusting its output, then judge every hit semantically. The batteries are probes, not the definition. Also read the densest prose in scope without a pattern in hand.
3. Fix owner-first: generated output → trace every consumer, fix the source or generator, then regenerate all derivatives; copied API text → owning declaration; paired documents → update both sides, copying verbatim blocks byte-for-byte into both; model- or user-visible strings → change only with behavior-backed evidence from the owning snapshot or e2e scenario, otherwise leave unchanged and report the deferral.
4. Before deleting anything, enumerate the passage's propositions per the complete-proposition rule and check the [overcorrection traps](references/examples.md#overcorrection-traps). Do not flip an obligation into an endorsement, promote a hypothetical to shipped behavior, delete a true fact, or drop provenance.
5. Re-run the batteries expecting only sanctioned keeps and calibration material. Confirm every remaining citation resolves in the current repository state and run the checks for every touched surface.
6. Report the inspected scope, fixes, sanctioned keeps, unresolved cases, and checks actually run.
