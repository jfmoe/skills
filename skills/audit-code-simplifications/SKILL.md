---
name: audit-code-simplifications
description: Find evidence-backed simplification candidates in an existing codebase when the user asks to remove dead or duplicated behavior, reduce speculative design, collapse unnecessary abstractions, remove redundant comments or implementation-heavy documentation, or replace hand-rolled infrastructure with a maintained dependency.
---

# Audit Code Simplifications

Turn a broad “find things to simplify” request into a few well-proven candidates that remove, fold, or demote existing surface area. This skill is guidance, not a checklist: follow the code, keep judgment active, and prefer a few well-proven candidates over a pile of thin guesses.

## Establish the current contract

Read the applicable repository instructions, architecture, current decision records, tests, and public documentation before judging a design. Treat documented seams and deliberate alternate implementations as intentional until evidence beats their rationale.

A simplification must identify what exists, who owns it, who currently consumes it, what obligation it serves, and what disappears if it changes.

## Strong candidates

A strong simplification removes, folds, or demotes something real and has clear evidence that the current design costs more than it buys:

- A public method, event, config knob, registry notification, helper, package, durable event, or test artifact has no production consumer.
- Tests or docs are the only consumers, and the behavior they pin is not load-bearing.
- Two representations mirror the same fact.
- A seam has methods every implementation must support but no consumer uses.
- A package or module exists only for test, demo, or support code and adds publication or dependency overhead.
- A feature implements speculative generality with no product owner or current consumer.
- An invariant, rollback path, expected output, or special-case test exists only to protect an unused API.
- An uncovered line or branch has no current contract or production consumer; the coverage failure is evidence for deletion, not a test to bolt on.
- Validation, fallback, or hostile-input tests protect values impossible under a typed same-process interface rather than an actual parser, configuration, model or tool JSON, durable-file, worker, process, or wire boundary.
- Hand-rolled code reimplements a maintained dependency or platform builtin, and the swap deletes the implementation plus its dedicated tests.
- The simplified behavior may differ slightly, but the new behavior remains reasonable and easier to explain.

Deleting a typo, running an unused-code tool once, reporting “this looks complex,” or removing an intentionally supported alternate implementation without consumer analysis is not a strong candidate.

### Audit invariant companions

Treat an invariant companion as useful only when it compares independently produced observations that can diverge. Remove empty installers and checks that merely inspect service presence, plugin metadata, fixed examples, or the result of calling the same mutation they claim to verify. For every omission, remove the export, build entry, invariant-only compiler reference or dependency, and companion-only test, then record the reason in the owning module's documentation or decision record. Keep a companion when it compares distinct event producers, durable history, or independently mutable data, even if the module also validates inputs synchronously.

## Survey broadly

Start with the largest production-code and lifecycle surfaces, not only unused-symbol output. Search across interfaces, implementations, configuration, dynamic loading, runtime strings, docs, tests, snapshots, and scripts.

For every defensive copy, freeze, validator, and callback capture, name where the value came from and who owns it next. Same-process typed calls ordinarily borrow typed values; parsers, configuration, queues, model or tool JSON, durable files, workers, processes, and wire decoders own or validate their data.

For asynchronous code, draw the ownership graph and map each sentinel, readiness promise, cancellation path, disposer, and state flag to a distinct owner or transition. Several mechanisms mirroring the same liveness or settlement fact are a candidate for one transaction or lifecycle controller. Preserve separate machinery when it protects publication rollback, callback containment, terminal-outcome arbitration, worker or process ownership, or disposal quiescence.

## Simplify prose with the code

Treat comments and documentation as maintained surface area. When trimming a passage, apply the complete-proposition rule: enumerate every proposition the passage carries, and each proposition that still holds must survive the trim.

- Delete comments that restate code or explain behavior owned elsewhere; keep required local contracts.
- Keep docs at their owning level; omit implementation details and rare cases unless they change a maintained contract.

## Hand-rolled code versus a dependency

Introducing a dependency is a valid simplification when it deletes owned code and tests.

- Name the exact hand-rolled surface the dependency covers. Residual semantics count against the swap.
- Check maintenance, adoption, security posture, license, platform support, and transitive footprint. Prefer platform builtins when the supported runtime already provides the capability.
- Weigh net deletion: implementation plus dedicated tests and docs, minus remaining glue.
- A wrapper that relocates the same complexity is not a win.
- Do not collapse a recorded architecture choice merely because a package exists; the replacement must beat the current rationale.

## Prove or reject each candidate

Classify consumers before writing:

- **Production:** runtime source, configuration, loaders, public APIs, and shipped entry paths.
- **Non-production:** tests, docs, decision records, snapshots, generated output, and comments.
- **Ambiguous:** examples and scripts that may be product smoke or release paths; inspect them before classifying.

Search the exact symbol, event, package, config key, method, and wire string, then read every material call site. Static unused-code tools help discovery but do not understand dynamic names, public interfaces, configuration, or product entry paths.

Existing tests describe behavior; they do not establish that the behavior remains required. When contract and consumer evidence shows behavior is obsolete, change or delete the behavior and its dedicated tests together. Do not preserve code solely to keep an obsolete test green or add tests solely to cover dead code.

Reject or downgrade a candidate when:

- a production caller exists and the change is a feature decision rather than cleanup;
- an active contract or hard-won defensive rule justifies it and new evidence does not beat that reason;
- removal creates unrelated churn without reducing public API or required behavior;
- the idea is correct but too local to deserve a durable design proposal.

## Report

For each accepted candidate, provide:

- the current owner and affected surface;
- production, non-production, and ambiguous consumer evidence;
- the exact deletion, fold, demotion, or replacement;
- behavior or capability given up;
- net code, test, documentation, dependency, and operational effects;
- risks and reintroduction conditions;
- observable acceptance criteria and the narrow checks that prove them.

Also report representative rejected candidates and why they failed the bar. Do not manufacture a candidate count.
