# 项目级产物来源

[English](SOURCES.md) | 中文

除非另有说明，所有上游路径和行号均指向 `deepseek-ai/deepseek-harness` 提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`。

| 产物 | 精确来源 |
|---|---|
| 项目根目录 `AGENTS*.review` | 根目录 `AGENTS.md` 第 83–93、99–143 行；`packages/AGENTS.md` 第 9–18 行；`packages/experimental/AGENTS.md` 第 5–9 行；`docs/development.md` 第 109–127 行；`apps/cli/config/agent-presets/cordis/skills/cordis-plugin-development/SKILL.md` 第 8–14 行中的“检查真实接口”原则。 |
| `subtrees/agent-products/AGENTS*.review` | `packages/AGENTS.md` 第 13–16 行；根目录 `AGENTS.md` 第 108、124–127 行；`apps/cli/config/agent-presets/cordis/skills/cordis-plugin-development/SKILL.md` 第 350–366 行。 |
| `subtrees/async/AGENTS*.review` | `docs/defensive-patterns.md` 第 7–25 行；`packages/AGENTS.md` 第 9、15 行。 |
| `subtrees/security-sensitive/AGENTS*.review` | `native/landlock-run/AGENTS.md` 第 9–16 行；`packages/web/AGENTS.md` 第 3–5 行；`docs/defensive-patterns.md` 第 27–33 行；`docs/subsystems/approval.md` 第 21–33、84–88 行；`vendor/AGENTS.md` 第 3–7 行。 |
| `subtrees/documentation/AGENTS*.review` | `docs/AGENTS.md` 第 7–17、34–45、59–75 行；用户明确要求排除格式政策。 |
| `subtrees/tests/AGENTS*.review` | 根目录 `AGENTS.md` 第 116、122 行；`docs/testing.md` 第 7–49 行；`examples/AGENTS.md` 第 7–18 行；`docs/cookbook/responding-to-pr-review-on-a-stack.md` 第 22 行；本地仓库 `AGENTS.md` 的“核心原则”章节中，以“绝对不要给文档、提示词等文本内容写单元测试”开头的条款。 |
| Hook、CI、配置和校验器 | `docs/development.md` 第 109–123 行；根目录 `AGENTS.md` 第 131 行；`website/AGENTS.md` 第 5–13 行；`vendor/AGENTS.md` 第 3–7 行；`docs/AGENTS.md` 第 41–43 行。 |

中文文件是忠实翻译。可执行和结构化产物使用中文说明对侧文件，不复制一套翻译后的可执行逻辑。
