# Fork upstream snapshots live in `registry/`, outside skill folders

A fork keeps its pristine upstream copy at `registry/upstream/<skill>/` — never inside the installable `skills/<category>/<skill>/` folder — and that snapshot's `SKILL.md` is renamed to `SKILL.md.orig`. We chose this because two `npx skills` behaviors (both verified) make the obvious alternative leak: it copies the *entire* skill folder, including dot-directories like a co-located `.upstream/`, into every project that installs the skill and offers no ignore/exclude option; and it discovers skills by the literal filename `SKILL.md` recursively, again with no ignore. So a pristine copy beside the fork would be shipped redundantly into every install, and a pristine `SKILL.md` anywhere in the repo would be wrongly registered as a second installable skill (and collide with the real fork).

## Considered Options

- **`.upstream/` inside the skill folder** — rejected: the whole folder, dot-dirs included, is copied into every install, leaking a redundant pristine `SKILL.md` that a runtime agent could misread.
- **Snapshot keeps the name `SKILL.md`** — rejected: discovered as an installable skill and collides with the real fork. Hence the `.orig` rename; diffing still works on content.
