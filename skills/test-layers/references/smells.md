# Test smells

Load on Review step 3. Each smell is a symptom of a Quality miss. Confirm it costs the suite, then change the tree disposition. Apply every section.

For each hit: smell, test, Quality item missed, new disposition.

## Fragile

**Symptom.** A behavior-preserving refactor forces test edits. Assertions track private fields, internal names, or collaborator call order.

**Quality.** Pin behavior.

**Keep when.** The implementation choice *is* the contract (served from cache, query uses an index). Name that guarantee.

## Change-detector

**Symptom.** Mocks and `verify` / `assert_called_with` with no assertion on a result. Production and test diffs have the same shape. Deleting it loses no input-output relationship.

**Quality.** Pin behavior. Independent oracle.

**Keep when.** A real-boundary interaction (email sent, charged exactly once) *is* the behavior.

## Obscure

**Symptom.** Several behaviors in one test, causal data off-stage, a giant fixture used in a sliver, or driving the unit through unrelated layers.

**Quality.** One behavior. DAMP.

**Keep when.** A real workflow *is* the unit. Size is the scenario.

## Assertion roulette

**Symptom.** Many bare assertions; a failure names a line, not a behavior.

**Quality.** One behavior.

**Keep when.** Several properties of *one* result (name, age, id on a parsed record) are one rule.

## Erratic

**Symptom.** Pass/fail with no code change: order, timing, wall clock, unseeded randomness, shared files or rows, sleeps as waits.

**Quality.** Isolated.

**Keep when.** Concurrency or randomness is the subject and the test controls it (seed, deterministic schedule). Real-system tests live in the slow suite.

## Duplication

**Symptom.** Copied setup or literals so one contract change edits many tests.

**Quality.** DAMP.

**Keep when.** Readable repetition makes the case obvious.

## Wrong thing

**Symptom.** Getters, config literals, `class_exists`, framework glue, utilities already exercised by a real caller, tests added to move coverage.

**Quality.** Load-bearing. Coverage.

**Keep when.** A reusable parser, date rule, or validation function has enumerable cases that could be wrong. A regulatory limit pins the behavior it protects.
