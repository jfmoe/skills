# The ledger is a single `ledger.yaml`, built by a pure core behind a thin shell

The registry sync is split into a deep, pure core (`build-ledger.mjs`) and a thin IO shell (`sync-registry.mjs`), and the two generated outputs (`registry/third-party.md` + `registry/inventory.json`) collapse into one `registry/ledger.yaml`.

The core exposes one function — `buildLedger(raw) -> yamlString` — plus the small parsers/classifier it is built from (`parseProjectsYaml`, `parseMetaYaml`, `isSelf`, `emitYaml`). It accepts a snapshot of already-read file *text* (the global lock, each project's lock, each fork's `meta.yaml`, plus `homeDir` and `repoRoot`) and returns the YAML string. Importing it runs nothing: no filesystem, no `process.env`, no side effects. The shell owns all IO — discover and read the files (reusing the core's `parseProjectsYaml` for project discovery), call `buildLedger`, write the file — and keeps the depth-robust `resolveRepoRoot` from ADR-0004. The CLI invocation is unchanged.

The text-snapshot boundary is the seam: it makes the whole pipeline (parse → classify self-vs-third-party → shape rows → render) testable without touching the disk or the network. The regression net for doing the split and the format change in one step is a golden/characterization test that feeds a captured live snapshot and asserts the assembled records equal the records the old script recorded in `inventory.json` — so the data is provably preserved across the format change, in place of a byte-for-byte diff (which is impossible when the format itself changes).

## Consequences

- One ledger, not two. The markdown was a human view and the JSON a machine view of the same data; maintaining both was duplicated rendering with no extra information. `ledger.yaml` is readable enough for humans and parseable enough for machines, carrying the full field set the JSON had (the markdown subset is gone).
- The YAML is produced by a small hand-rolled emitter with zero runtime dependencies. Its one rule — every scalar is double-quoted and escaped — removes all "does this value need quoting" heuristics; empty sections render as `key: []`.
- Tests live in a repo-root `test/` directory with a `private` root `package.json` (`npm test` → `node --test`), never inside a skill folder, because `npx skills` copies a skill folder wholesale into every install. `build-ledger.mjs` itself does ship — it is the skill's own code.

## Considered Options

- **Keep the two outputs, just extract a core** — rejected: the dual format was itself the redundancy; extracting a core without collapsing the outputs would have preserved two renderers of one dataset.
- **Pull in a YAML library** — rejected: violates the zero-runtime-dependency rule. Our output shape is small and regular, so a ~20-line emitter covers it.
- **Byte-for-byte diff as the regression net** — rejected: the format changes in this step, so there is no stable byte baseline; the golden test asserts on the data instead.
