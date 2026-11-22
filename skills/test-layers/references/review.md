# Reviewing a suite

Load when reviewing, pruning, or speeding up a suite. The three rules and the layer tree live in [SKILL.md](../SKILL.md).

## Steps

1. Label every test in scope by what it *starts* (in-process, HTTP, child process, database, browser). Done: every test has a label.
2. Walk the layer tree. Disposition: `keep` / `demote` / `native+fixture` / `delete`. Done: every test has a disposition with its layer and rule.
3. Check every test against every row of [Smells](#smells). Done: each hit names the smell, the test, and the new disposition.
4. When the goal is speed, time each test and split its time into setup, waiting, and the rule under test. Done: every slow test has its time attributed, and fixes are ranked by time saved against change cost.
5. Propose `demote` and `delete`; edit after agreement. Done: the proposed set matches the dispositions.

**Delete with evidence.** Same oracle, same input class, no extra fault class. Identical line coverage can still hide two oracles.

## Smells

A smell is a symptom. Confirm it costs the suite before changing the disposition.

| Smell | Symptom | Keep when |
| --- | --- | --- |
| Fragile | A behavior-preserving refactor forces test edits. Assertions track private fields, internal names, or collaborator call order. | The implementation choice *is* the contract (served from cache, query uses an index). Name that guarantee. |
| Change-detector | Mocks and `verify` / `assert_called_with` with no assertion on a result. Production and test diffs have the same shape. Deleting it loses no input-output relationship. | A real-boundary interaction (email sent, charged exactly once) *is* the behavior. |
| Tautological | The expected value is computed the way production computes it; the production formula used twice is one computation, not a check. | Never. Replace the expected value with a literal, a spec value, or a worked example. |
| Obscure | Several behaviors in one test, causal data off-stage, a giant fixture used in a sliver, or driving the unit through unrelated layers. | A real workflow *is* the unit. Size is the scenario. |
| Assertion roulette | Many bare assertions; a failure names a line, not a behavior. | Several properties of *one* result (name, age, id on a parsed record) are one rule. |
| Erratic | Pass/fail with no code change: order, timing, wall clock, unseeded randomness, shared files or rows, sleeps as waits. | Concurrency or randomness is the subject and the test controls it (seed, deterministic schedule). Real-system tests live in the slow suite. |
| Slow | Most of a test's time goes to setup or waiting rather than the rule: a shared workflow run before every test, a real deadline slept through, one process per row of a rule table. | The time *is* the boundary (a real kill, a real network deadline) and few tests pay it. |
| Duplication | Copied setup or literals so one contract change edits many tests. | Readable repetition makes the case obvious: inputs and expected outputs stay in the test body. |
| Wrong thing | Getters, config literals, `class_exists`, framework glue, utilities already exercised by a real caller, tests added to move coverage, tests asserting a retired behavior is rejected or absent. | A reusable parser, date rule, or validation function has enumerable cases that could be wrong. A regulatory limit pins the behavior it protects. |
