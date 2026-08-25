# Artifact index

English | [中文](ARTIFACT_INDEX.zh.md)

The canonical mapping is `ARTIFACT_INDEX.tsv`. It contains 45 derived artifact pairs. Every row names:

- the canonical English or executable artifact;
- its Simplified Chinese counterpart or Chinese explanation;
- the source record that lists exact upstream paths and line ranges;
- the pair kind used by the verifier.

Raw files under `upstream/repository/` and pristine files under `artifacts/registry/upstream/` are source evidence, not derived artifacts. Provenance files named `SOURCES.md` and language-neutral TSV inventories are metadata rather than prompt deliverables.

The verifier rejects any derived artifact that is missing from the index, any missing counterpart or source record, duplicate index entries, mismatched Skill names, and Markdown pairs whose heading hierarchy or fenced code differs.
