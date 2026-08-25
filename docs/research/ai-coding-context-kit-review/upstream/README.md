# Pinned upstream evidence

English | [中文](README.zh.md)

This tree mirrors the selected AI-coding instruction corpus from `deepseek-ai/deepseek-harness` at commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`.

File contents are byte-identical to the upstream Git blobs. Discovery-sensitive basenames are renamed only in the mirror:

- `SKILL.md` → `SKILL.md.orig`
- `AGENTS.md` → `AGENTS.md.orig`
- `CLAUDE.md` → `CLAUDE.md.orig`
- root `LICENSE` → `LICENSE.orig`

The original path, mirrored path, blob SHA, line count, kind, and disposition are recorded in `../audit/source-manifest.tsv`.

Upstream symlinks are represented as regular mirror files containing the byte-identical Git link blob. This preserves the source hash without creating a renamed symlink that would point at an active or nonexistent basename.

These files are evidence rather than derived artifacts. They have no translated copies because a translation would not be the pinned source. Derived English and Chinese candidates live under `../artifacts/`.
