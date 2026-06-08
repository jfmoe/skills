# Config Editing & Provider/Model Workflow

Stable mechanics for changing Hermes's configuration safely, plus the ordered workflow for switching providers/models so the change actually takes effect. Specific keys, sections, and provider names are **not** listed here — they go stale. Discover them live (see pointers below).

> Before running any command, confirm its flags with `hermes <cmd> --help` (SKILL.md Rule 2). If something here doesn't cover your case, fetch the docs index (Rule 1).

## Safe config-editing norms (adopted from Hermes's bundled autonomous-ai-agents skill)

Source: the bundled skill (see SKILL.md machine facts) and the local docs page `~/.hermes/hermes-agent/website/docs/user-guide/skills/bundled/autonomous-ai-agents/`.

- **Use the dedicated commands, not blind YAML editing.** `hermes config edit` opens the file in `$EDITOR`; `hermes config set KEY VAL` sets a single value (dotted keys, e.g. `section.key`). These keep the file valid and avoid clobbering structure.
- **Settings vs secrets are separate stores.** Non-secret settings live in `config.yaml`; API keys and tokens live in `.env`. Find the paths with `hermes config path` and `hermes config env-path`.
- **API keys go through `hermes auth`** (the credential manager / pool), not hand-edited `.env`. Don't print keys in plaintext and never commit them to any repo.
- **Validate after editing:** `hermes config check` (missing/outdated config) and `hermes config migrate` (pull in new options / migrate deprecated settings). Retiring specific deprecated models is a separate, narrower command — `hermes migrate` (currently `hermes migrate xai`); run `hermes migrate --help` to see what it currently covers.
- **`security.redact_secrets` is on by default** and snapshotted at startup. Toggling it mid-session (even via an env var from a tool call) does NOT affect the running process — change it from a terminal, then start a new session. This is intentional, so the agent can't turn off redaction on itself.
- **`approvals.mode`:** `manual` (default; prompts before destructive shell commands) / `smart` (auxiliary LLM auto-approves low-risk) / `off` (skips all prompts, same as `--yolo`). Per-invocation bypass: `hermes --yolo …`. YOLO/`off` does NOT disable secret redaction.
- **Restart to apply.** A config edit only takes effect in a fresh process: exit and relaunch the CLI, or `/restart` the gateway. (Full restart mapping for tool/skill/source changes: `reference/troubleshooting.md`.)

> **The list of config sections, keys, defaults, and current values is not copied here** — it's the most stale-prone thing. To see what exists and what's set: read `~/.hermes/config.yaml` directly, or run `hermes config show`. For the full annotated reference, read the local doc `~/.hermes/hermes-agent/website/docs/user-guide/configuration.md` (web mirror: `https://hermes-agent.nousresearch.com/docs/user-guide/configuration`).

## Provider / model workflow (ordered — this is the stable part)

The point of ordering: a model/provider switch only "works" if the credential exists first and the process is restarted after. Do these in order.

1. **Configure the provider's credential first.** `hermes auth` (interactive) or `hermes auth add <provider>`. If you select a provider in the model picker before its credential is set up, it'll only fail at runtime. Verify with `hermes auth list` / `hermes auth status`.
2. **Select the default model / provider.** `hermes model` (interactive picker; `--refresh` re-fetches each provider's live model list). The persistent provider lives in `config.yaml` under `model.provider`.
3. **Configure fallback** (tried when the primary model fails — rate-limit, overload, connection errors). `hermes fallback --help` for `add` / `list` / `remove` / `clear`.
4. **Restart so it takes effect.** Exit and relaunch the CLI, or `/restart` the gateway.
5. **Verify what's actually live.** `hermes status` (add `--all` for a redacted full view) and `hermes model` confirm which provider/model is in effect — don't assume the edit took.

> **The provider list and their env-var / auth methods are not copied here** (they change often). To see what's available and how each authenticates: run `hermes model`, or read the local doc `~/.hermes/hermes-agent/website/docs/integrations/providers.md` (web mirror: `https://hermes-agent.nousresearch.com/docs/integrations/providers`). For a one-off override without changing config: `hermes -m <model> --provider <provider> …` (see `hermes chat --help`).
