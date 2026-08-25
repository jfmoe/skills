# Skills Repository

The personal source repository for user-created agent skills. It holds editable Original and Fork skill sources, plus the provenance needed to compare Forks with their upstream versions.

## Skill classes

**Original**:
A skill written entirely in this repo, with no upstream ancestor. Lives at `skills/<skill>/`.
_Avoid_: custom, homegrown

**Fork**:
A third-party skill that has been modified here. Kept as two copies — the installable modified copy at `skills/<skill>/`, and a pristine upstream snapshot at `registry/upstream/<skill>/`.
_Avoid_: patched, vendored, customized

**Third-party**:
A skill used unmodified from an external source. It stays outside this repository and is neither Original nor Fork.
_Avoid_: external, vendor, dependency

## Management surfaces

**Upstream snapshot**:
The unmodified upstream files of a fork, kept under `registry/upstream/<skill>/` for diffing when upstream changes. Its `SKILL.md` is renamed to `SKILL.md.orig` so it is never installed.
_Avoid_: vendor copy, baseline, original
