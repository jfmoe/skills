# Validation report

English | [中文](validation-report.zh.md)

Validated on 2026-08-22 against `deepseek-ai/deepseek-harness` commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`. All required checks passed.

## Checks

| Surface | Result and evidence |
|---|---|
| Pinned upstream corpus | All 70 `source-manifest.tsv` rows matched paths, blob SHAs, line counts, and bytes in the pinned Git tree. The verifier passed both offline mode and `--upstream <clone>` mode, which rederives the tree comparison rather than trusting the manifest. |
| Discovery completeness | The pinned tree contains 21 files under the 11 repository Skill directories, 10 shipped-preset files, and 26 standing instruction or discovery entrypoints; the manifest misses none. `prompt-surface-scan.tsv` exactly matches all 125 paths selected by the expanded discovery rule. |
| Symlink handling | Five `CLAUDE.md` link blobs equal `AGENTS.md`; `.claude/skills` equals `../.agents/skills`. The mirror preserves those raw blobs as regular `.orig` files. The review bundle contains no actual symlink. |
| Derived artifact pairing | `ARTIFACT_INDEX.tsv` contains 45 English/executable and Chinese/explanatory pairs. Every target and source record exists; Markdown heading hierarchies and fenced code blocks match; derived relative links resolve. |
| Candidate Skills | Skill Creator's `quick_validate.py` passed 7 of 7 promotion copies in an isolated Python environment. All seven `agents/openai.yaml.review` files parse, have 25–64 character English descriptions, and mention the correct `$skill-name`. |
| Pristine fork snapshots | All 12 proposed snapshot files match their pinned upstream files byte-for-byte. This includes the full independent `dsh-trim-cot-leakage` Skill, examples, and recall batteries. |
| Hook and CI implementation | Node syntax checks passed for all three scripts, `sh -n` passed for the hook, 23 YAML files parsed, and the JSON configuration parsed. The guardrail smoke passed five scenarios: staged success, staged-deletion isolation, protected rename rejection, one-sided projection rejection, and base-to-HEAD success. |
| Text and discovery isolation | Derived files have exactly one final newline and no trailing whitespace. No literal active `SKILL.md`, `AGENTS.md`, or `CLAUDE.md` exists in the bundle. `npx skills add /Users/jfmoe/Coder/skills --list` still finds only the repository's existing 11 live Skills. |
| Workspace boundary | Every task path is under `docs/research/ai-coding-context-kit-review/`. The only status entry outside that directory is the user's pre-existing `registry/ledger.yaml`; its Git blob stayed `5e3725a3f8b21b5d6466ebd74d44605a2b1fc1dc`. |

## Corrective findings from self-review

- Expanded discovery found five active `CLAUDE.md` symlinks and the `.claude/skills` discovery symlink that the initial filename rule omitted. They are now mirrored, classified, and covered by the verifier; the final counts are 70 sources and 125 scan paths.
- The Chinese rendering of “fail closed” had incorrectly used the separate concept “fail fast.” It now says default deny in the security instruction and both audit ledgers.
- A source-to-artifact comparison found three testing rules underrepresented in the candidate prompts: obsolete behavior changes with its tests, uncovered code may be dead, and impossible hostile inputs do not belong at typed same-process boundaries. They are now explicit in project/test instructions and the simplification, review, and check-selection Skills.
- `dsh-trim-cot-leakage` remains a complete independent candidate unit: Skill, UI metadata, examples, recall batteries, their Chinese counterparts, and bilingual provenance. Its three pristine upstream files are separately preserved.
- Empty legacy `project/`, `skills/`, `user/`, and `registry/` directory trees were removed after confirming they contained no files.

## Remaining review boundary

Mechanical checks cannot prove that a portable policy choice is desirable for a particular target repository or that every translation nuance is ideal. Human review should compare each candidate with its sibling `SOURCES.md`, the disposition and clause ledgers, and the pinned mirror before promotion. Nothing in this bundle is installed, active, promoted, or committed by this validation.
