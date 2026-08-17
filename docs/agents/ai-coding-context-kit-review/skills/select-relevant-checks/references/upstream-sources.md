# Upstream sources

This skill is a portable fork of DeepSeek Harness `dsh-pre-push-checks`, supplemented by its testing policy. Upstream repository: `deepseek-ai/deepseek-harness`, commit `47f943859bef60e4160492346772ded9b24f765a`.

## Source map

| Skill material | Upstream source and position | Preservation |
|---|---|---|
| Inspect the outgoing change | `.agents/skills/dsh-pre-push-checks/SKILL.md`, lines 10-25 | Workflow preserved; exact Git and DeepSeek `change-scope` commands are generalized. |
| Narrowest relevant evidence | Same file, lines 27-37 | Opening rule and check classes are substantially verbatim with package names removed. |
| Coverage selection | Same file, lines 39-60 | Core distinction and anti-bypass rule retained without Vitest-specific commands. |
| Full local rehearsal | Same file, lines 62-64 | Verbatim except the removed DeepSeek aggregate name. |
| Real implementation, world verification, and real entry | `docs/testing.md`, lines 21-35 | Principles preserved and generalized. |
| Snapshot requirement | `docs/testing.md`, lines 47-49 | Converted from a universal project mandate into conditional evidence selection. |

Pinned source links:

- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-pre-push-checks/SKILL.md#L10-L64>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/testing.md#L7-L49>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/AGENTS.md#L86-L92>

## Portable changes

Removed DeepSeek commands, fixed coverage threshold, Git stack rewriting, force-push mechanics, and CI lane names. Added an explicit no-remote-mutation boundary and UI verification branch.

`agents/openai.yaml` preserves the upstream thin-wrapper pattern from `.agents/skills/dsh-pre-push-checks/agents/openai.yaml`, lines 1-4, with the portable Skill name and purpose substituted.

Pinned wrapper: <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-pre-push-checks/agents/openai.yaml#L1-L4>

## License

MIT License

Copyright (c) 2026 DeepSeek

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
