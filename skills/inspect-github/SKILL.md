---
name: inspect-github
description: Read and analyze GitHub content with the gh CLI. Use whenever the target is any GitHub-hosted remote content or repository.
---

# Inspect GitHub

Use `gh` commands as the default interface for GitHub content.

- Prefer purpose-built commands such as `gh repo view`, `gh pr view`, `gh issue view`, and `gh api` over unauthenticated HTTP fetching.
- For repository analysis, create a directory with `mktemp -d`, shallow-clone with `gh repo clone OWNER/REPO TEMP/REPO -- --depth 1`, and inspect the local checkout.
- Fetch additional refs or history only when the task requires them.
