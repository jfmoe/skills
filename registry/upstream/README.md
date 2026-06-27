# Upstream Snapshots (for forks)

A **fork** is a third-party skill you modified. It has two copies:

- **Installable, modified copy** — `skills/<category>/<skill>/SKILL.md`. Kept clean: no
  upstream files, no management metadata. `npx skills` copies the whole skill folder into
  every project that installs it, so nothing extra belongs here.
- **Pristine upstream snapshot** — `registry/upstream/<skill>/` (this directory). The
  unmodified upstream files, kept for diffing when upstream changes.

## Layout

```text
registry/upstream/<skill>/
  SKILL.md.orig     # pristine upstream SKILL.md, RENAMED (see below)
  ...               # other upstream files, as-is (references/, scripts/, ...)
  meta.yaml         # provenance
```

`meta.yaml`:

```yaml
source: owner/repo                 # upstream github source (or URL)
ref: main                          # branch or tag fetched
commit: <sha>                      # exact commit fetched
upstream_path: path/in/source      # skill subpath inside the source repo
local_path: skills/coding/<skill>  # the modified copy in this repo
fetched_at: 2026-06-27             # fetch date
notes: |
  - what was changed / removed
```

## Why `SKILL.md.orig` instead of `SKILL.md`

`npx skills` discovers skills by the literal filename `SKILL.md` **anywhere** in the repo,
and has no ignore/exclude option (both verified). A pristine `SKILL.md` here would be wrongly
registered as an installable skill and could even collide with the real fork. So rename every
`SKILL.md` inside a snapshot to `SKILL.md.orig`. Diffing still works on content.

Forks are surfaced in the generated ledger (`registry/third-party.md`) by scanning the
`meta.yaml` files here.
