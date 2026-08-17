# Upstream sources

This skill is a portable fork of DeepSeek Harness `dsh-prose-standard`, supplemented by its documentation placement rules. Upstream repository: `deepseek-ai/deepseek-harness`, commit `47f943859bef60e4160492346772ded9b24f765a`.

## Source map

| Skill material | Upstream source and position | Preservation |
|---|---|---|
| Objective and definition of contract | `.agents/skills/dsh-prose-standard/SKILL.md`, lines 8-12 | Opening paragraph and comment rule are verbatim. |
| Scope, write authority, and derivative exclusions | Same file, lines 14-26 | Authority semantics retained; DeepSeek paths and bilingual workflow removed. |
| Complete proposition | Same file, lines 28-42 | Core list is preserved with related result and safe-use facts coalesced. |
| Prose surfaces | Same file, lines 38-61 | General semantic requirements retained; DeepSeek document names and links generalized. |
| One home per fact and current-state prose | `docs/AGENTS.md`, lines 15-45 | Semantic placement rules retained; formatting, budgets, bilingual pairing, and exact document taxonomy excluded. |
| Reasoning transcript leakage | `docs/AGENTS.md`, lines 59-71; `.agents/skills/dsh-trim-cot-leakage/SKILL.md`, lines 8-23 and 39-45 | Examples generalized while retaining the keep-contract/delete-derivation distinction. |
| Distilled calibration examples | `.agents/skills/dsh-prose-standard/references/examples.md`, lines 1-167 | Example body retained verbatim; only a navigation table was added. |
| OpenAI wrapper | `.agents/skills/dsh-prose-standard/agents/openai.yaml`, lines 1-4 | Thin-wrapper pattern retained with the portable Skill name and scope substituted. |

Pinned source links:

- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-prose-standard/SKILL.md#L8-L61>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/AGENTS.md#L15-L45>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-trim-cot-leakage/SKILL.md#L8-L45>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-prose-standard/references/examples.md#L1-L167>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-prose-standard/agents/openai.yaml#L1-L4>

## Portable changes

Removed Markdown layout, word budgets, exact document tiers, bilingual pairing, Agent Note lifecycle, and DeepSeek paths. Kept semantic completeness, single ownership, current-state documentation, Skill-scope requirements, prose-surface coverage, reasoning-transcript rules, and the upstream calibration examples.

`agents/openai.yaml` preserves the upstream thin-wrapper pattern from `.agents/skills/dsh-prose-standard/agents/openai.yaml`, lines 1-4, with the portable Skill name and scope substituted.

## License

MIT License

Copyright (c) 2026 DeepSeek

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
