---
name: test-layers
description: Layer tests at the cheapest proof of their rule. Use when writing tests, reviewing or pruning a suite, or judging fragile, change-detector, or over-mocked tests.
---

# Test Layers

A test *pins* one **rule** at one **layer**, with an independent **oracle**. Writing → Write. Reviewing → Review.

## Write

1. Name the rule (which bug goes *red*) and the oracle. Done: both are written down.
2. Walk the [tree](#tree). Write one test at that layer. Done: the test sits on the chosen layer.
3. Apply every [Quality](#quality) item. Done: every item holds.

## Review

1. Label every test in scope by what it *starts* (in-process, HTTP, child process, database, browser). Done: every test has a label.
2. Walk the [tree](#tree). Disposition: `keep` / `demote` / `native+fixture` / `delete`. Done: every test has a disposition with its layer and rule.
3. Apply every smell in [smells](references/smells.md). Done: every smell checked; each hit names the smell, the test, the Quality item missed, and the new disposition.
4. Propose `demote` and `delete`; edit after agreement. Done: the proposed set matches the dispositions.

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

**in-process.** Public API of the unit; fake the next I/O hop. Calculation, queuing, mapping, validation.

**boundary.** Exercise that process, wire, or OS fact for real. Few. HTTP authz, kill/crash isolation, browser journeys that need JS or visual state.

**native.** One real execute of the engine. Map fields from a fixture.

Start **in-process**. Escalate when the rule *is* the boundary or a native engine result.

## Quality

Apply every item.

**Pin behavior.** Assert returns, errors, and visible side effects at the public interface. Internal call order only when that order is the contract (charge once, serve from cache); name the guarantee.

**Independent oracle.** A literal, a spec, or a worked example. The production formula used twice is one computation, not a check.

**DAMP.** Inputs and expected outputs stay in the body. Extract duplication that would force a synchronized structural edit.

**One behavior.** One rule per test, named for the guarantee. Shared setup and assertion → one table. Distinct failure mode → separate test. An input the production code does not branch on stays in the table.

**Isolated.** Any order, same result. Inject clock, seed, and I/O at the boundary. Quarantine or fix flakes.

**Load-bearing.** Test what the team could get wrong. Framework, config literals, and getters are covered by the behavior they drive.

**Coverage.** Unexecuted code is a lead. An assertion that would go red if the operator flipped pins the rule.

**Delete with evidence.** Same oracle, same input class, no extra fault class. Identical line coverage can still hide two oracles.

## Examples

- Queue / concurrency cap → in-process (stub the compute slot).
- Timeout kills work; crash leaves no partial row → boundary (real process).
- Domain object → JSON → in-process (fixture).
- HTTP authz → boundary (one real request). Handler calculation → in-process.
- Browser journey that needs JS → boundary.
