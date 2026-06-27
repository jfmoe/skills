# Skills live in a flat tree with no category directories

Every skill lives at `skills/<skill>/SKILL.md` — one flat level. There are no `coding/` or `workflows/` (or any other) category directories, and none are to be added. This **reverses** the previously documented rule that categories were limited to `skills/workflows/` and `skills/coding/`; that rule lived in `AGENTS.md` (never an ADR), so it is recorded here to stop a future review re-introducing the two-level layout.

We removed the category level because it carried no leverage: the `coding`/`workflows` split was a shallow grouping that the tooling never read (`npx skills` and `sync-registry.mjs` both discover skills by walking for `SKILL.md`, not by category), while it cost real coupling — the category appeared in every skill's path and was restated across `AGENTS.md`, `CONTEXT.md`, `README.md`, the manage-skills docs, `projects.yaml`, the fork `meta.yaml` `local_path`s, and the sync script's repo-root resolution. Flattening is the prefactor for the ledger refactor: with skills flat, the sync script's repo-root resolution no longer depends on directory depth (it walks up for the dir holding both `registry/` and `skills/`), and the many path references stabilize at `skills/<skill>/`. Make the change easy, then make the easy change.

## Consequences

- If grouping is ever needed again, it will be frontmatter metadata on the skill, not a directory level — metadata can be queried without moving files or rewriting paths.
- The sync script resolves the repo root by walking up for a directory that contains both `registry/` and `skills/`, instead of counting a fixed number of `../` levels, so it keeps working wherever a skill folder is nested.
- Fork `meta.yaml` `local_path`s and the generated ledger record flat `skills/<skill>` paths.

## Considered Options

- **Keep `coding`/`workflows` categories** — rejected: the split was never load-bearing for any tool, added a restated coupling point across the whole repo, and the routing rule ("ops troubleshooting → workflows, automation code → coding") was a judgement call that produced no behavior.
- **Replace categories with new directory groupings** — rejected: any directory taxonomy re-creates the same coupling. Defer grouping to frontmatter metadata if a real need appears.
