# Upstream Snapshots (for forks)

This directory holds the **pristine upstream snapshot** of each fork — the unmodified
upstream files of a third-party skill you modified, kept for diffing when upstream changes.
The clean, installable copy of the fork lives separately at `skills/<skill>/SKILL.md`.

## Layout

```text
registry/upstream/<skill>/
  SKILL.md.orig     # pristine upstream SKILL.md, renamed (see ADR-0001)
  ...               # other upstream files, as-is (references/, scripts/, ...)
  meta.yaml         # provenance (schema lives in the canonical home — see below)
```

## See also

- **Fork procedure (create + update) and the `meta.yaml` schema** — the `manage-skills`
  skill (`skills/manage-skills/SKILL.md`), the single canonical home (ADR-0006).
- **Why the snapshot's `SKILL.md` is renamed to `SKILL.md.orig`** — ADR-0001.
