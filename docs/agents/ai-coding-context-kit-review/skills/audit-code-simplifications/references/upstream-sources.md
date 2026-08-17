# Upstream sources

This skill is a portable fork of DeepSeek Harness `dsh-find-simplifications`. Upstream repository: `deepseek-ai/deepseek-harness`, commit `47f943859bef60e4160492346772ded9b24f765a`.

## Source map

| Skill material | Upstream source and position | Preservation |
|---|---|---|
| Objective and evidence threshold | `.agents/skills/dsh-find-simplifications/SKILL.md`, lines 8 and 17-31 | Guidance and evidence-threshold sentences and most candidate bullets are verbatim; only DeepSeek-specific nouns, examples, links, and Agent Note thresholds are removed or generalized. |
| Survey breadth | Same file, lines 33-45 | The stop condition and production-delta warning are verbatim; the DeepSeek subsystem inventory and unconditional subagent routing are excluded. |
| Consumer classification and proof | Same file, lines 64-80 | Classification and reject conditions are preserved with repository path names generalized. |
| Trust and lifecycle audit | Same file, lines 47-51 | Both paragraphs are substantially verbatim; service/plugin names and DeepSeek boundary examples are generalized. |
| Dependency as simplification | Same file, lines 53-62 | The dependency proof and net-deletion standard are substantially verbatim; DeepSeek-settled dependencies, package manager, engine floor, and Agent Notes are generalized. |
| Current owner and consumer requirement | `packages/AGENTS.md`, lines 9-12 | Preserved as evidence requirements. |

Pinned source links:

- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-find-simplifications/SKILL.md#L8-L80>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/AGENTS.md#L9-L12>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/AGENTS.md#L111-L121>

## Portable changes

Removed DeepSeek-specific protected twin adapters/backends, Agent Note creation and consolidation, PR folding, exact repository paths, and local validation commands. Retained general survey, trust/lifecycle, dependency-proof, consumer-proof, and reject-condition wording wherever it remains true outside DeepSeek. Added an explicit read-only authority rule and portable output classes.

`agents/openai.yaml` was generated from this portable skill. There is no upstream wrapper for `dsh-find-simplifications`; the new one-sentence `$audit-code-simplifications` prompt is original and intentionally contains no workflow duplication.

## License

MIT License

Copyright (c) 2026 DeepSeek

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
