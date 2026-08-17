# Sources for `agent-guardrails.config.json`

Upstream: `deepseek-ai/deepseek-harness` at `47f943859bef60e4160492346772ded9b24f765a`. License notice: [`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

The JSON schema and implementation are original. Its three policies are extracted from these locations:

| Config field | Source and position | Derived policy |
|---|---|---|
| `artifactSourcePairs` | User requirement for this kit; DeepSeek `docs/AGENTS.md`, lines 15-34 | Give each maintained fact or artifact one explicit owner and source record, including every AGENTS template shipped under `subtrees/`. |
| `protectedPathPrefixes` | `vendor/AGENTS.md`, lines 3-7; `.agents/notes/archived/AGENTS.md`, lines 3-7 | Protect vendored and frozen paths mechanically only after a project explicitly configures them. |
| `sourceProjectionPairs` | `website/AGENTS.md`, lines 5-11; `.agents/skills/dsh-doc-site-sync/SKILL.md`, lines 8 and 21-27 | A generated projection may change only with its canonical source or owning generator workflow. |

Pinned links:

- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/AGENTS.md#L15-L34>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/vendor/AGENTS.md#L3-L7>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/notes/archived/AGENTS.md#L3-L7>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/website/AGENTS.md#L5-L11>
- <https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/.agents/skills/dsh-doc-site-sync/SKILL.md#L8-L27>

## Configuration

`protectedPathPrefixes` entries use:

```json
{
  "prefix": "path/to/frozen-area",
  "allowPrefixes": ["path/to/frozen-area/manifest.md"],
  "reason": "Use the owning synchronization workflow"
}
```

`sourceProjectionPairs` entries use:

```json
{
  "sources": ["docs", "scripts/generate-docs.mjs"],
  "projections": ["website/generated"],
  "reason": "Regenerate the website projection from canonical docs"
}
```

Prefixes are repository-relative path components, not globs. Empty policy arrays are deliberate: project-specific ownership must not be guessed by a portable template.
