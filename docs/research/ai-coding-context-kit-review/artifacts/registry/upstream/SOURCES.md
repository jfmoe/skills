# Sources for proposed fork snapshots

English | [中文](SOURCES.zh.md)

Every pristine file in this directory is copied byte-for-byte from commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`. The source-to-destination mapping is:

| Candidate | Upstream path |
|---|---|
| plan-code-changes | `apps/cli/config/agent-presets/standard/agent.cordis.yml` |
| audit-code-simplifications | `.agents/skills/dsh-find-simplifications/**` |
| review-code-changes | `.agents/skills/dsh-code-review/**` |
| select-relevant-checks | `.agents/skills/dsh-pre-push-checks/**` |
| apply-documentation-standards | `.agents/skills/dsh-doc-standards/**` |
| review-code-prose | `.agents/skills/dsh-prose-standard/**` |
| trim-cot-leakage | `.agents/skills/dsh-trim-cot-leakage/**` |

Each `meta.yaml` follows the fork schema in the local `manage-skills` Skill. Its Chinese companion explains the same values but is not registry input.
