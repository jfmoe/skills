# Skills live in a flat tree with no category directories

Every skill lives at `skills/<skill>/SKILL.md` — one flat level. There are no `coding/` or `workflows/` (or any other) category directories, and none are to be added. This **reverses** the previously documented rule that categories were limited to `skills/workflows/` and `skills/coding/`; that rule lived in `AGENTS.md` (never an ADR), so it is recorded here to stop a future review re-introducing the two-level layout.

We removed the category level because it carried no leverage: the `coding`/`workflows` split was a shallow grouping that `npx skills` never read, while it cost real coupling — the category appeared in every skill's path and was restated across `AGENTS.md`, `CONTEXT.md`, `README.md`, the manage-skills docs, and fork `meta.yaml` files. Flattening stabilizes those references at `skills/<skill>/`.

## Consequences

- If grouping is ever needed again, it will be frontmatter metadata on the skill, not a directory level — metadata can be queried without moving files or rewriting paths.
- Fork `meta.yaml` files record flat `skills/<skill>` paths.

## Considered Options

- **Keep `coding`/`workflows` categories** — rejected: the split was never load-bearing for any tool, added a restated coupling point across the whole repo, and the routing rule ("ops troubleshooting → workflows, automation code → coding") was a judgement call that produced no behavior.
- **Replace categories with new directory groupings** — rejected: any directory taxonomy re-creates the same coupling. Defer grouping to frontmatter metadata if a real need appears.
