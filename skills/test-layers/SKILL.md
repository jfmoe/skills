---
name: test-layers
description: Layer tests at the cheapest proof of their rule. Use when writing tests, reviewing or pruning a suite, speeding up a slow suite, or judging fragile, change-detector, or over-mocked tests.
---

# Test Layers

A test *pins* one **rule** at one **layer**, with an independent **oracle**. Writing → Write. Reviewing → Review.

## Write

1. Name the rule (which bug goes *red*) and the oracle. Done: both are written down.
2. Walk the [tree](#tree). Write one test at that layer. Done: the test sits on the chosen layer; a boundary test names the fact in-process cannot observe.
3. Apply every [Quality](#quality) item. Done: every item holds.
4. Run the test and read its runtime. Done: the runtime is known, and every slow second belongs to the rule or its boundary fact.

## Review

1. Label every test in scope by what it *starts* (in-process, HTTP, child process, database, browser). Done: every test has a label.
2. Walk the [tree](#tree). Disposition: `keep` / `demote` / `native+fixture` / `delete`. Done: every test has a disposition with its layer and rule.
3. Apply every smell in [smells](references/smells.md). Done: every smell checked; each hit names the smell, the test, the Quality item missed, and the new disposition.
4. When the goal is speed, time each test and split its time into setup, waiting, and the rule under test. Done: every slow test has its time attributed, and fixes are ranked by time saved against change cost.
5. Propose `demote` and `delete`; edit after agreement. Done: the proposed set matches the dispositions.

## Tree

```text
What rule does this test pin?
  A cheaper layer already pins the same input class, failure mode, and oracle?
    yes → stop
    no  → where does a real failure appear?
          same-process logic                         → in-process
          process, signal, wire, crash, frozen input → boundary
          third-party engine native result           → native
```

**in-process.** Public API of the unit; fake the next I/O hop. Calculation, queuing, mapping, validation, state machines, persistence rules (a real temporary store counts as in-process).

**boundary.** Exercise that process, wire, or OS fact for real. A rule that merely *passes through* a boundary is not a boundary rule: pin the rule in-process, then keep a few representative boundary paths per boundary, not one per rule. HTTP authz, kill/crash isolation, browser journeys that need JS or visual state.

**native.** One real execute of the engine. Map fields from a fixture. Query semantics, rendering, and other engine results stay native; a fake never stands in for them.

Start **in-process**. Escalate when the rule *is* the boundary or a native engine result.

## Quality

Apply every item.

**Pin behavior.** Assert returns, errors, and visible side effects at the public interface. Internal call order only when that order is the contract (charge once, serve from cache); name the guarantee.

**Independent oracle.** A literal, a spec, or a worked example. The production formula used twice is one computation, not a check.

**DAMP.** Inputs and expected outputs stay in the body. Extract duplication that would force a synchronized structural edit.

**One behavior.** One rule per test, named for the guarantee. Shared setup and assertion → one table. Distinct failure mode → separate test. An input the production code does not branch on stays in the table.

**Minimal setup.** Setup builds only what the rule reads. Prepare state directly instead of running an unrelated workflow (installation, full service startup, login, a UI path) to reach it; that workflow has its own tests.

**Isolated.** Any order, same result. Inject clock, seed, and I/O at the boundary; deadlines advance on the injected clock. Before asserting that something did *not* happen, wait for a signal that processing finished. Quarantine or fix flakes.

**Load-bearing.** Test what the team could get wrong. Framework, config literals, and getters are covered by the behavior they drive. A retired behavior leaves with its tests; the removal itself is the evidence, so no test asserts the old command, field, or route is now rejected or absent.

**Coverage.** Unexecuted code is a lead. An assertion that would go red if the operator flipped pins the rule.

**Delete with evidence.** Same oracle, same input class, no extra fault class. Identical line coverage can still hide two oracles.

## Examples

- Queue / concurrency cap → in-process (stub the compute slot).
- Timeout kills work; crash leaves no partial row → boundary (real process).
- Timeout *classification* (late result becomes "unknown") → in-process (fake clock).
- No duplicate work after restart → in-process (reopen the same store).
- Domain object → JSON → in-process (fixture).
- HTTP authz → boundary (one real request). Handler calculation → in-process.
- Browser journey that needs JS → boundary. Error text for each failure cause → in-process component test.
