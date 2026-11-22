---
name: ub-mode
description: >
  Engineering principles for the implementer: first make it work, then make it
  right. Use when implementing a ticket or changing code, and as a standards
  source when reviewing a change.
---

# ub-mode

Written for the implementer. Every time you are asked to make a change follow:
* First Make it Work.
* Then Make it Right.
* Follow Practice

When a principle pulls against the spec, or reaches past the scope of your task, ask whoever gave you the task before acting on it.

# First Make it Work

## Laziness Protocol

* One decision lives in one place.
* Ship the smallest edit that solves the problem.

## Foundational Thinking

* Get the data shape right before you write the logic.
* Do first whatever helps every later phase.
* If a concurrent writer would matter, do not share state.

## TDD

* Write the failing test before you change the code.
* See it fail for the reason you expect.
* Make the smallest change that makes it pass.
* If an honest test is impractical, do not write a bad one.

## Redesign From First Principles

* Do not bolt a new requirement onto the old design.
* Ask what you would have built if it had been there from the start, think that through, and deliver it in pieces.

## Attack the Premise

* When two fixes that share one premise fail the same gate, write that premise in one sentence and count which actors hold the imbalance.
* Remove the assignment.
* Do not start another fix until you have done that.

## Subtract Before You Add

* Take complexity out before you add anything.

## Outcome-Oriented Execution

* Aim at the end state you can check.
* A break in the middle is allowed when you planned it and can undo it.

## Build the Lever

* If the work is not obvious at a glance, build the tool that does it.
* Do one unit by hand, then make the tool match that unit.

## Architecture

### Model the Domain

* Put the domain in a structure that makes the illegal states impossible.
* Maintain a glossary of domain terms.
* If the code is already clear and local, leave it.

### Boundary Discipline

* Check the data where it enters.
* Inside, trust it.
* Keep the business logic in a pure function.

### Type System Discipline

* Make the illegal value impossible to write.
* Parse outside data once, where it comes in.
* Do not silence the compiler.

### Make Operations Idempotent

* Running it twice, or running it after a crash halfway through, ends in the same state.

### Separate Before Serializing Shared State

* If they do not need the same mutable thing, give each its own.
* If they do, allow one writer, and enforce that in the structure.

# Then Make it Right

## Fix Root Causes

* Reproduce it.
* Fix the cause.
* A guard that only hides the crash is not a fix.

## Sequence work into verifiable units

* Finish one small unit and check it.
* Then start the next.

## Test Behavior, Not Implementation

* The test calls the code the way its user does and checks the result that user would see.
* If the test would still pass when every function returned nothing, throw it out.

## Optional Metrics

* Run a metric tool (CRAP score, duplication, mutation testing) only when the project declares it in `docs/agents/quality-gates.md`. No file means no metrics.
* Every result is a lead to investigate. There is no coverage goal.
* Uncovered code: delete it when nothing in production uses it. Test it only when you can name the bug that would turn the test red.
* High CRAP: split the function or delete it before considering a test.
* Duplication: merge only what you have shown to be one piece of knowledge.
* Surviving mutant: kill it with an assertion on behavior a caller sees, or delete the code it lives in. An equivalent mutant needs neither.

## Refactoring

* Pin what the code does.
* Change the structure.
* Prove the behavior did not change.

# Practice

## Commit

* Keep structural change and behavioral change in separate commits.
* A refactor commit leaves what each test expects as it was, and the checks pass before and after it.
