# 固定上游证据

[English](README.md) | 中文

本目录镜像了 `deepseek-ai/deepseek-harness` 提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` 中选定的 AI 编程指令语料。

文件内容与上游 Git blob 逐字节一致。镜像只修改可能触发发现机制的文件名：

- `SKILL.md` → `SKILL.md.orig`
- `AGENTS.md` → `AGENTS.md.orig`
- `CLAUDE.md` → `CLAUDE.md.orig`
- 根目录 `LICENSE` → `LICENSE.orig`

原始路径、镜像路径、blob SHA、行数、类别和处置方式记录在 `../audit/source-manifest.tsv` 中。

上游符号链接在镜像中表示为普通文件，内容与 Git 链接 blob 逐字节一致。这样既能保留来源哈希，也不会创建指向生效文件名或不存在文件名的重命名链接。

这些文件属于证据，不是派生产物，因此没有翻译副本；翻译后将不再是固定版本原文。派生的中英文候选产物位于 `../artifacts/`。
