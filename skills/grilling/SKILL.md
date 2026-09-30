---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding of every **one-way door** in the plan. Map this as a **design tree**: every decision branches into the decisions that hang off it.

## Sort every node

Sort each node before it reaches the user. Only one-way doors become questions.

- **Fact**: something the environment holds (code, config, docs, tools, history). Finding facts is your job, never the user's: dispatch a sub-agent to look it up. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report.
- **Observable**: an answer you can see by running something (behavior, timing, output, layout). Settle it with a throwaway spike or prototype and bring back the evidence.
- **Two-way door**: reversible, cheap to change later, or an implementation detail. Decide it yourself and list it under the round's **Defaults**. Raise an edge case only when there is evidence it occurs.
- **One-way door**: a goal, a scope boundary, a product or preference call, or a choice expensive to reverse. These are the user's: put each to them and wait.

## Design forks

When a one-way door is a choice of shape (who owns what, how data flows, where the boundaries sit), ground yourself in the code first, then offer 2–3 **whole-shape candidates** in place of a string of point questions. Candidates differ in structure, not in parameters, and each is one you would defend. Put them in one comparison table: the essence in one line, who owns what, the cost, and when it is the wrong choice. Recommend one. The user may pick one or graft ("B, with C's X").

Once a shape is picked, the decisions inside it are two-way doors for Defaults unless one is itself a one-way door.

## Rounds

Work the tree in **rounds**. The **frontier** is every one-way door whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Open each question with one or two plain sentences of background: what exists now and why the choice matters. Use the user's own terms, and define any term they haven't used.

Close each round with the Defaults you took since the last round. The user overrides any by number; their reply settles the rest, so the round still waits for it.

Format a round like so:

```
❓ **Q1** - **<question title>**: <background, then the question; may hold multiple choices or a candidate table>

➡️ <your recommended answer>

---

❓ **Q2** - ...

---

**Defaults** (override by number):

| # | Decision | Default | Why |
|---|---|---|---|
| D1 | <decision> | <what you chose> | <one line> |
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock nodes that depended on them. Re-sort the new nodes, recompute the frontier, and ask the next round. A frontier holding only two-way doors earns no round of its own; carry them to the closing summary.

## Done

The session is done when no one-way door remains open. Close with a summary: every decision settled, every Default taken, and one line per two-way door deferred to implementation, where the code will settle it. Do not act on it until the user confirms you have reached a shared understanding.
