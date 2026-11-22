---
name: test-layers
description: Layer tests at the cheapest proof of their rule. Use when writing tests, reviewing or pruning a suite, speeding up a slow suite, or judging fragile, change-detector, or over-mocked tests.
---

# Test Layers

A test *pins* one **rule** at one **layer**, against an independent **oracle**.

1. **Name the red.** Before writing a test, write down which bug turns it *red* and where the expected value comes from: a literal, a spec, a worked example. With no such bug, there is no test: framework glue, config literals, and getters are covered by the behavior they drive. Unexecuted code is a lead to a rule, and coverage is no reason for a test.
2. **Cheapest layer.** Pin the rule at the cheapest layer where that failure can be observed, and pin it once.
3. **Assert what the caller sees.** Returns, errors, and visible side effects at the public interface, so a behavior-preserving refactor leaves the test untouched.

Reviewing or pruning a suite, or speeding one up → follow [references/review.md](references/review.md).

## Layers

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

**boundary.** Exercise that process, wire, or OS fact for real, and name the fact in-process cannot observe. A rule that merely *passes through* a boundary is not a boundary rule: pin the rule in-process, then keep a few representative boundary paths per boundary, not one per rule. HTTP authz, kill/crash isolation, browser journeys that need JS or visual state.

**native.** One real execute of the engine. Map fields from a fixture. Query semantics, rendering, and other engine results stay native; a fake never stands in for them.

Start **in-process**. Escalate when the rule *is* the boundary or a native engine result.

A seam and a layer are separate choices: the seam is which interface the test calls, the layer is how much real machinery it starts. A module's highest seam, driven in-process with the next I/O hop faked, satisfies both.

## While writing

**One rule per test**, named for the guarantee. Shared setup and assertion → one table. Distinct failure mode → separate test. An input the production code does not branch on stays in the table.

**Call order only as contract.** Assert internal call order only when that order is the guarantee (charge once, serve from cache); name the guarantee.

**Minimal setup.** Setup builds only what the rule reads. Prepare state directly instead of running an unrelated workflow (installation, full service startup, login, a UI path) to reach it; that workflow has its own tests.

**Isolated.** Any order, same result. Inject clock, seed, and I/O at the boundary; deadlines advance on the injected clock. Before asserting that something did *not* happen, wait for a signal that processing finished. Quarantine or fix flakes.

**Retired behavior leaves with its tests.** The removal itself is the evidence, so no test asserts the old command, field, or route is now rejected or absent.

**Read the runtime.** Run the test; every slow second belongs to the rule or its boundary fact.

## Examples

- Queue / concurrency cap → in-process (stub the compute slot).
- Timeout kills work; crash leaves no partial row → boundary (real process).
- Timeout *classification* (late result becomes "unknown") → in-process (fake clock).
- No duplicate work after restart → in-process (reopen the same store).
- Domain object → JSON → in-process (fixture).
- HTTP authz → boundary (one real request). Handler calculation → in-process.
- Browser journey that needs JS → boundary. Error text for each failure cause → in-process component test.
