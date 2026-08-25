# Sources and portable changes

English | [中文](SOURCES.zh.md)

## Exact upstream source

- Primary: `apps/cli/config/agent-presets/standard/agent.cordis.yml`, commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`, lines 113–124.
- Duplicate prompt copies reviewed: `code/agent.cordis.yml` lines 120–131 and `cordis/agent.cordis.yml` lines 101–112.
- Supporting ownership and evidence rules: root `AGENTS.md` lines 87–93 and `packages/AGENTS.md` lines 10–16.

## Preserved wording

The “Explore first,” “Resolve discoverable facts,” and “Make the plan decision-complete” paragraphs retain the upstream wording, with only product-specific tool names and presentation mechanics removed.

## Portable changes

- Removed `exit_plan_mode`, `todo_write`, request-cache, and fixed tool-catalog mechanics because they depend on the DeepSeek runtime.
- Replaced the runtime-specific exit protocol with the portable completion criterion “return the complete plan and remain read-only.”
- Expanded the plan fields only with clauses already required by upstream review, package, and testing instructions.
- Added a Simplified Chinese translation. It adds no workflow rule.

Pristine source: `../../../upstream/repository/apps/cli/config/agent-presets/standard/agent.cordis.yml`.
