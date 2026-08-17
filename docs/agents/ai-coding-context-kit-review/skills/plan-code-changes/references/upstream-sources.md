# Upstream sources

This skill is a portable fork of the plan-mode prompt in DeepSeek Harness's standard Agent preset. Source repository: `deepseek-ai/deepseek-harness`, commit `47f943859bef60e4160492346772ded9b24f765a`. The complete pristine `agent.cordis.yml` that owns the prompt is retained under `registry/upstream/plan-code-changes/`.

## Source map

| Skill material | Upstream source and position | Preservation |
|---|---|---|
| Read-only plan mode and repository exploration | `apps/cli/config/agent-presets/standard/agent.cordis.yml`, lines 113-120 | The “Use non-mutating reads…” paragraph is verbatim. The discoverable-facts paragraph is preserved except that the product-specific `ask_user_question` tool name is generalized. |
| Decision-complete plan | `apps/cli/config/agent-presets/standard/agent.cordis.yml`, line 122 | Verbatim except that the introductory imperative is moved into the section heading. |
| Explicit plan approval and no implementation during planning | `apps/cli/config/agent-presets/standard/agent.cordis.yml`, lines 113-124 | General approval and later-implementation sentences are verbatim; `exit_plan_mode`, `todo_write`, and cache-stability mechanics are generalized or removed because they are not portable tools. |
| Prefer current owners, consumers, and existing patterns | `packages/AGENTS.md`, lines 9-12; `.agents/skills/dsh-code-review/SKILL.md`, lines 31-35 | Adapted into planning questions. |

Pinned source links:

- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/apps/cli/config/agent-presets/standard/agent.cordis.yml#L113-L124>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/AGENTS.md#L9-L12>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-code-review/SKILL.md#L31-L35>

`agents/openai.yaml` was generated from this skill. Its one-sentence `$plan-code-changes` wrapper follows the thin default-prompt pattern used by DeepSeek workflow skills; it does not duplicate the workflow body.

## License

MIT License

Copyright (c) 2026 DeepSeek

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
