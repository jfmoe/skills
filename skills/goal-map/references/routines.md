# Routines

The recurring touchpoints a secretary keeps with the user. Each routine works the same whether the user asks for it or a schedule starts it. Write permissions and the draft format follow `SKILL.md`. Write to the user in Chinese, briefly, as one message.

## Morning brief

Help the user decide what today is for.

1. Gather: open LIFE issues due today or overdue (the due-date query in `SKILL.md`); open issues of the active LIFE cycle (`linear issue query --team LIFE --cycle active --state unstarted --state started --json`); `等待` issues whose follow-up date has arrived; habits behind pace for the week.
2. Suggest at most three focus items for today, with a one-line reason each, and mention what is overdue.

When nothing is due, overdue, or behind, reply that there is nothing for today and stop.

## Evening check-in

Close the day's loop.

1. List what today's brief suggested and any issue due today that is still open.
2. Ask what got done. On the reply, mark reported issues done and add habit check-ins directly. For each slipped item, ask briefly why, and offer a new date, a smaller step, or dropping it.

When nothing was planned or due today and no habit is behind, reply that there is nothing to check and stop.

## Weekly review (end of week)

Look back on the active LIFE cycle before it ends; its open issues will roll over. Gather evidence before judging:

1. **Linear**: the active cycle's completed and open issues; habit counts from check-in comments; each active initiative with its projects and latest updates; projects completed or canceled this week.
2. **GitHub**: for each `github:` line of started DEV projects and of DEV projects that changed this week, its sub-issues (`gh api repos/<owner>/<repo>/issues/<number>/sub_issues --paginate`) closed this week with their `state_reason`, and merged PRs (`gh pr list -R <owner>/<repo> --state merged --search "merged:>=<date>" --limit 100`). When a list reaches its limit, say the data may be incomplete.
3. **Budget**: the counts described in `SKILL.md`.

Then write the review:

- Wins: what moved each goal, with evidence.
- Per goal: measure now versus target (ask for any value missing from the past week), `onTrack|atRisk|offTrack` with a one-line reason, and the next project or step.
- Slipped and stale: issues that will roll over, projects past target date, `等待` items. Ask why for anything that slipped twice.
- Budget line.

Save it as document `周回顾 <YYYY>-W<ww>` attached to the active LIFE cycle by its number; when `document list --team LIFE --cycle <number> --json` already has that title, update it instead. Send the review with one numbered draft covering: a status update per active initiative and started project, unfinished habit issues to cancel, and DEV projects that look shipped (per `dev-projects.md`).

Done when every active initiative has a drafted update and the document's identifier is reported.

## Weekly planning (start of week)

Agree on the new cycle with the user.

1. Read the latest weekly review and what the user approved from it. When there is no active initiative, open with an offer to set goals together (vision, then areas, then one to three goals) per `SKILL.md` before planning issues.
2. When the week's capacity is unknown (travel, deadlines elsewhere), ask once.
3. Propose the cycle's issues, ranked by goal deadline, dependency, and effort: at most 10 in total, counting rolled-over issues and the habit issues to create. Name what you deferred and why.

After confirmation, move the agreed issues into the cycle and create the habit issues for that cycle per `SKILL.md`.

## Monthly check (start of month)

- Per initiative: an initiative update draft and a check that its measure is still the right one.
- Projects: started projects past their target date, and finished phases to close.
- Ideas: each idea older than a month, with a suggested outcome (one action, a project or goal, keep, or drop) per `SKILL.md`.
- Budget: counts, plus the oldest open backlog issues as close candidates.
- Vision: ask whether `愿景与领域` still holds when a goal was completed or dropped this month.
