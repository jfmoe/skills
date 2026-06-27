# Manage fork upstreams by manual diff-and-port, not git subtree/submodule

Forks track their upstream with a plain file snapshot (`registry/upstream/<skill>/`) plus `meta.yaml` provenance (`source`, `ref`, `commit`, `upstream_path`, `local_path`, `fetched_at`, `notes`). Updating a fork is a three-way operation done by hand: fetch a fresh upstream, diff it against the stored snapshot to see what changed, port the wanted changes into the modified copy, then refresh the snapshot and `meta.yaml`. We deliberately rejected git subtree and submodules, and we do not auto-merge upstream into forks.

## Considered Options

- **git subtree / submodule** — rejected: couples the installable skill folder to external VCS machinery, when `npx skills` only needs a plain folder, and buys little because forks intentionally diverge from upstream.
- **Automatic merge of upstream into the fork** — rejected: a fork exists precisely to deviate, so which upstream changes to take is a judgement call; the diff is surfaced and a human picks.
