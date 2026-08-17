# Upstream sources

This skill is a portable fork of DeepSeek Harness `dsh-code-review`. Upstream repository: `deepseek-ai/deepseek-harness`, commit `47f943859bef60e4160492346772ded9b24f765a`.

## Source map

| Skill material | Upstream source and position | Preservation |
|---|---|---|
| Guidance boundary, live range, surrounding context, and review priority | `.agents/skills/dsh-code-review/SKILL.md`, line 8 | The guidance sentence and review-priority sentence are verbatim; the DeepSeek `change-scope` command and PR-only nouns are generalized. |
| Semantic review axes | Same file, lines 31-45 | Most bullet wording is verbatim. Cordis, Loader-export, invariant, Agent Note, transcript, and bilingual specifics are removed or generalized. |
| Prose review | Same file, lines 20-27 | Semantic-review requirement retained without repository-specific documentation tiers. |
| Finding contract | Same file, lines 47-49 | First four sentences are substantially verbatim; GitHub-thread mechanics removed. |
| Defensive bug classes | `docs/defensive-patterns.md`, lines 7-33 | Referenced through the lifecycle, boundary, and teardown axes. |

Pinned source links:

- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-code-review/SKILL.md#L8-L49>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/defensive-patterns.md#L7-L33>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/AGENTS.md#L9-L16>

## Portable changes

Removed exact DeepSeek commands, Cordis registration invariants, Agent Note lifecycle, bilingual documentation checks, snapshot names, and GitHub reply mechanics. Added explicit read-only authority and an empty-review rule.

`agents/openai.yaml` was generated from this portable skill. There is no upstream wrapper for `dsh-code-review`; the new one-sentence `$review-code-changes` prompt is original and intentionally contains no workflow duplication.

## License

MIT License

Copyright (c) 2026 DeepSeek

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
