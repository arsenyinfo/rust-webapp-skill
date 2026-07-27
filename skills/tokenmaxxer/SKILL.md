---
name: tokenmaxxer
description: Serious engineering work behind a reviewed plan and adversarial review gates. The required first argument word picks the mode - `build`, `refactor`, `sweep`, `experiment`, or `followup`. Invoke explicitly, e.g. `/tokenmaxxer refactor <component>`.
argument-hint: "build <task>  |  refactor <component>  |  sweep <area>  |  experiment <goal>  |  followup"
compatibility: "requires an external review tool (e.g. codex:codex-rescue or opencode); the investigate skill is recommended for deep triage (a self-contained core ships in references/triage.md); sweep additionally needs the gh CLI and a git repo with a remote; experiment additionally needs a runnable eval command in the target repo"
---

Serious work mode. Task: $ARGUMENTS

The dev loop is the same across modes: understand the problem, capture intent in a contract, implement in reviewable slices, validate, and run adversarial review gates. What differs is *who approves*, *what may change*, and *how work is chunked* — that lives in the mode file.

## Mode dispatch

The first word of `$ARGUMENTS` names the mode and is **required — there is no default**. It is always a mode selector, never part of the task, so a task that happens to start with the word "refactor" or "sweep" is never misread. If the first word is not exactly one of the five below, do not guess the mode — tell the user it is required and ask which one. Requiring the keyword is a safety property, not a formality: `sweep` opens PRs while the user is asleep, so it must never be reached by inference.

**Attended — these compose on `build`. Read `references/build.md` (the dev loop) plus your mode's own file (the overrides).**

- **`build <task>`** → `references/build.md`. A feature, a root-caused bug fix, or a broad cross-cutting change — a codebase-wide refactor-shaped change (a rename, a pattern migration) included.
- **`refactor <component>`** → `references/refactor.md`. Consolidate one component that grew by accretion into one coherent design; behavior-preserving. One component — codebase-wide is `build`.
- **`followup`** → `references/followup.md`. Work the run doc's open follow-ups with the user's decisions, review-first. No required argument; an optional one names an older run doc or filters by area.

**Autonomous — each stands alone. Never load either beside another mode's file.**

- **`sweep <area>`** → `references/sweep.md`. Unattended overnight cleanup of a named area, shipping tiny verified fixes as draft PRs.
- **`experiment <goal>`** → `references/experiment.md`. Metric-driven experimentation toward a goal: frame the metric and noise floor, build a hypothesis tree, gate and get it approved, run the batch autonomously, report with the next batch proposed.

## Supervision matrix

| mode | approver | consent boundary | escalation → | composition |
|---|---|---|---|---|
| `build` | user | plan approval | ask the user | the base loop |
| `refactor` | user | plan approval | ask the user | build + overrides |
| `followup` | user | per-item decision at intake | ask the user | build + overrides |
| `sweep` | none — unattended | the named area, fixed at launch | run doc → *needs-your-call* | standalone |
| `experiment` | user at the ends only | the approved hypothesis tree | attended phases: ask · mid-batch: ambiguity → disclosed best guess; scope, contract, or frozen protocol → park as a next-batch proposal | standalone |

**Never operate under two modes' policies at once.** That blend is the failure this skill guards against. Attended modes pause and ask; `sweep` never asks once launched (its one question — refusing to start without a named area — happens at launch); `experiment` is attended at the ends and autonomous mid-batch strictly under the pre-approved plan, which is its consent boundary as the named area is sweep's.

This matrix is the whole supervision policy; the mode file adds detail under its own row and never contradicts it. The shared references (`design-taste.md`, `deletion-evidence.md`, `triage.md`) carry mechanisms and evidence standards only, never policy.

## Working doc

Every run keeps **one** working doc at `/tmp/tokenmaxxer-<repo-basename>-<mode>-<slug>-<YYYYMMDD-HHMM>.md` — intent contract, progress, follow-ups, and outcome in one place. The timestamp keeps a repeated run from overwriting an earlier one's undrained findings. The path is convention, not memory: after compaction or in a fresh session, find the doc by globbing `/tmp/tokenmaxxer-<repo-basename>-*` — never guess the exact name. Two modes open no doc of their own: build's trivial fast path (unless it surfaces a follow-up), and `followup`, which works in the doc it drains.

There is no cross-run ledger. Findings live with the run that found them, and `followup` works one doc at a time — by default the most recently modified one that still has `open` or `deferred` blocks, so a later run that left none cannot shadow it. Format and the follow-up block spec are in `references/core.md`.

## Next

Read `references/core.md` — the review gates, intent contract, escalation mechanism, and working doc format shared by every mode — then your mode's file, and follow them.
