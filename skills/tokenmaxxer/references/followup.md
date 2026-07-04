# followup mode

You are in **followup** mode: work through the follow-up ledger — out-of-scope findings recorded by earlier runs (router, Follow-up ledger) — with the user's decisions, review-first. No argument is needed: the ledger path is derived from the repo by convention. An optional argument filters entries by area/path or names a specific ledger or sweep-report file to draw from.

This mode runs the **build** workflow (`references/build.md`) for every approved item — its gates govern the dev cycle; the sections below specialize intake and shipping. It is attended: every entry here was recorded precisely because it needs a human decision, so nothing ships without one.

## Intake

1. Read the ledger at the router's path convention. If it is missing or has no `open`/`deferred` entries, check surviving sweep reports (`/tmp/sweep-report-*`) for *needs-your-call*/*Incomplete* entries that never reached a ledger and import them; absent those too, report there is nothing to follow up and stop.
2. **Re-verify before asking.** Ledger evidence goes stale: PRs merge, code moves. Check each entry against the current default branch — confirm the defect still exists at (or near) the recorded location. An entry that no longer reproduces is marked `dropped (resolved elsewhere)` with one line of evidence; never bring a dead item to the user.
3. **Decisions first, execution second.** Present the surviving items grouped by subsystem, each as its recorded decision question plus recommendation; the user answers fix / skip / defer per item. Collect the whole batch before implementing anything, so a long session never splits a decision from its context.

## Execution

- Each *fix* item is a build-workflow task seeded by its entry: the evidence is the triage (established when the entry was recorded and re-verified at intake — do not re-investigate a proven mechanism), and the user's answer is the approval of intent. Build's trivial fast path applies on build's own criteria; the external diff gate is never skipped.
- An item that is really an accreted-component consolidation is not absorbed here: recommend a `refactor <component>` run and mark the entry `deferred` to it.
- An *Incomplete* leftover (a verified branch whose push or PR-creation failed, with its recorded command and error): confirm with the user, then finish exactly the recorded step — never re-implement work that already passed its gates.
- Ship per subsystem: approved items touching one subsystem ride one branch → one draft PR, each item its own commit, its `sweep-key` line in the PR body — so CI runs once per subsystem and the next sweep's dedup suppresses everything handled here.

## Close the loop

Update the ledger in the same run: `done (PR)` for shipped items, `dropped (reason)` for skips, `deferred` for the rest. Out-of-scope findings discovered *during* follow-up work are appended as new `open` entries per the router's rule — follow-ups spawn follow-ups; the ledger after the run is the queue for the next one.
