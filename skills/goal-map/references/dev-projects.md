# Dev projects

Keep DEV projects in step with the requirements tracked on GitHub. GitHub tickets stay the unit of work; a DEV project is the goal-level handle for one independent requirement.

## When a PRD or wayfinder map is published

Run this after the repository's issue tracker workflow (`to-spec`, `wayfinder`) creates the GitHub issue.

1. Find the project: `linear project list --team DEV --json`, matching a `github:` line in a description or an obviously identical name.
2. When the new issue only supplements a found project's scope, append its `github:` line to that project's description with `linear project update <id> --description`. When it would push the description past 255 characters or changes the done criteria, tell the user what to edit in the overview instead.
3. When it is an independent requirement, propose a project: name, summary, done criteria, target date, goal, repo label. After confirmation:

   ```bash
   linear project create --team DEV --name "<requirement name>" \
     --description "github: <owner>/<repo>#<number>" \
     --content-file <overview.md> --status planned \
     --target-date <YYYY-MM-DD> --label "repo:<repo-name>" \
     --initiative "<goal>"
   ```

   The overview follows the format in `SKILL.md`. Omit `--initiative` when no goal was agreed; link one later with `linear initiative add-project <initiative> <project>`.
4. When the PRD defines phases, add milestones: `linear milestone create --project <id> --name <phase> --target-date <date>`.

Done when the project carries every `github:` line and you have reported it by name.

## Sync from GitHub

The weekly review runs this with the GitHub facts it gathered:

- Set a `planned` project to `started` once any of its tickets has closed or a PR has merged.
- When a milestone's tickets are all closed as completed, post `linear project-update create <id> --health onTrack --body-file <file>` naming the merged PRs.

## When the requirement looks shipped

When every sub-issue under the project's `github:` issues is closed, or the user says it shipped, gather the evidence: each close reason (`completed` or `not_planned`), the merged PRs, and the overview's done criteria. Propose one outcome:

- **Completed**: the done criteria are met by merged work.
- **Canceled**: the work was closed as not planned or replaced.
- **Ask**: the evidence is mixed.

After confirmation, post a final project update listing what shipped and any follow-up issues left open on GitHub, then set the status.

Completing a project leaves its initiative untouched; the goal is judged in the weekly review against its measure.
