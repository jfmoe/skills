# Sources for project artifacts

English | [中文](SOURCES.zh.md)

Unless stated otherwise, every upstream path and line range refers to `deepseek-ai/deepseek-harness` commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`.

| Artifact | Exact source |
|---|---|
| Root project `AGENTS*.review` | Root `AGENTS.md` lines 83–93, 99–143; `packages/AGENTS.md` lines 9–18; `packages/experimental/AGENTS.md` lines 5–9; `docs/development.md` lines 109–127; `apps/cli/config/agent-presets/cordis/skills/cordis-plugin-development/SKILL.md` lines 8–14 for the “inspect the real interface” principle. |
| `subtrees/agent-products/AGENTS*.review` | `packages/AGENTS.md` lines 13–16; root `AGENTS.md` lines 108, 124–127; `apps/cli/config/agent-presets/cordis/skills/cordis-plugin-development/SKILL.md` lines 350–366. |
| `subtrees/async/AGENTS*.review` | `docs/defensive-patterns.md` lines 7–25; `packages/AGENTS.md` lines 9, 15. |
| `subtrees/security-sensitive/AGENTS*.review` | `native/landlock-run/AGENTS.md` lines 9–16; `packages/web/AGENTS.md` lines 3–5; `docs/defensive-patterns.md` lines 27–33; `docs/subsystems/approval.md` lines 21–33, 84–88; `vendor/AGENTS.md` lines 3–7. |
| `subtrees/documentation/AGENTS*.review` | `docs/AGENTS.md` lines 7–17, 34–45, 59–75; user requirement to exclude formatting policy. |
| `subtrees/tests/AGENTS*.review` | Root `AGENTS.md` lines 116 and 122; `docs/testing.md` lines 7–49; `examples/AGENTS.md` lines 7–18; `docs/cookbook/responding-to-pr-review-on-a-stack.md` line 22; local repository `AGENTS.md`, section `核心原则`, the clause beginning “绝对不要给文档、提示词等文本内容写单元测试”. |
| Hook, CI, config, and verifier | `docs/development.md` lines 109–123; root `AGENTS.md` line 131; `website/AGENTS.md` lines 5–13; `vendor/AGENTS.md` lines 3–7; `docs/AGENTS.md` lines 41–43. |

The Chinese files are faithful translations. Executable and structured artifacts use Chinese explanatory companions rather than translated executable copies.
