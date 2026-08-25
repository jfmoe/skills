# The fork procedure has one canonical home; other surfaces are pointers

The fork procedure (the create and update flows) and the `meta.yaml` schema live in exactly one place — the `manage-skills` skill, `skills/manage-skills/SKILL.md`. Every other surface points at it instead of restating it:

- `AGENTS.md` keeps only the fork *invariants* (a fork is two copies; the snapshot's `SKILL.md` is renamed to `SKILL.md.orig`) plus a one-line pointer to the canonical procedure. The how-to steps and the `meta.yaml` field enumeration are gone.
- `registry/upstream/README.md` keeps only the snapshot directory's physical layout plus pointers — procedure and schema to `SKILL.md`, the `.orig` rationale to ADR-0001.

Before this, the procedure and schema were restated across three documents. That smeared one concept across three files: changing the procedure or a `meta.yaml` field meant editing all three and hoping they stayed in sync, and they had already drifted (the schema's per-field comments existed only in `registry/upstream/README.md`, the steps only in `SKILL.md`, a partial field list only in `AGENTS.md`). Consolidating gives the concept locality — one place to read it, one place to change it — and makes `manage-skills` the deep module that owns "how forks work" rather than a thin restatement competing with two others.

## Consequences

- Changing the fork procedure or the `meta.yaml` schema is a one-file edit in `skills/manage-skills/SKILL.md`. The per-field schema comments that used to live in `registry/upstream/README.md` were absorbed there so nothing was lost.
- `AGENTS.md` and `registry/upstream/README.md` are now pointers; a reviewer who finds procedure detail creeping back into them should move it to the canonical home.

## Considered Options

- **Leave the procedure restated in three places** — rejected: it had already drifted, and three copies of one procedure is exactly the shallow, smeared shape this repo's domain work is trying to remove.
- **Move the procedure into an ADR** — rejected: ADRs record *why* a decision was made, not the operational *how*. The how-to belongs with the skill that performs it; the what/why split (glossary in `CONTEXT.md`, the `.orig` rationale in ADR-0001) is deliberate and stays.

## Scope guard

This consolidates only the *procedural* duplication. `CONTEXT.md` (the glossary) and ADR-0001 (the `.orig` rationale) are deliberately left untouched — that what / why / how split is intentional.
