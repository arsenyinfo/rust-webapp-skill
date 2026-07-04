---
name: tokenmaxxer
description: Serious engineering work with a reviewed plan and adversarial review gates; the required first argument word picks the mode. `build` — features, root-caused fixes, cross-cutting changes (trivial ones skip planning, never the diff gate). `refactor` — consolidate one accreted component, behavior-preserving. `sweep` — unattended overnight cleanup of a named area, shipped as draft PRs. `experiment` — metric-driven experimentation: approved hypothesis tree, autonomous batch of runs, next-batch report. `followup` — work recorded out-of-scope findings with the user's decisions; no required argument. Invoke explicitly, e.g. `/tokenmaxxer refactor <component>`.
argument-hint: "build <task>  |  refactor <component>  |  sweep <area>  |  experiment <goal>  |  followup"
compatibility: "requires an external review tool (e.g. codex:codex-rescue or opencode); the investigate skill is recommended for deep triage (a self-contained core ships in the triage reference); all modes use the design-taste and triage references, refactor/sweep add deletion-evidence; sweep additionally needs the gh CLI and a git repo with a remote; experiment additionally needs a runnable eval command in the target repo"
---

Serious work mode. Task: $ARGUMENTS

The dev loop is the same across modes: understand the problem, capture intent in a contract, implement in reviewable slices, validate, and run adversarial review gates. What differs is *who approves*, *what is allowed to change*, and *how work is chunked* — that lives in the mode file.

## Mode dispatch

The first word of `$ARGUMENTS` names the mode and is **required — there is no default**. It is always a mode selector, never part of the task, so a task that happens to start with the word "refactor" or "sweep" is never misread.

- **`build <task>`** → `references/build.md`. A feature, a root-caused bug fix, or a broad cross-cutting change — a codebase-wide refactor-shaped change (a rename, a pattern migration) included.
- **`refactor <component>`** → `references/refactor.md`. Consolidate a component that grew by accretion into one coherent design; behavior-preserving. One component — codebase-wide is `build`.
- **`sweep <area>`** → `references/sweep.md`. Unattended overnight cleanup of a named area, shipping tiny verified fixes as draft PRs.
- **`experiment <goal>`** → `references/experiment.md`. Metric-driven experimentation toward a goal: frame the metric and noise floor, build a hypothesis tree, gate and get it approved, run the batch autonomously, report with the next batch proposed.
- **`followup`** → `references/followup.md`. Work through the follow-up ledger (below) with the user's decisions, review-first. No required argument; an optional one filters by area or names a specific ledger/report file.

If the first word is not exactly one of `build`, `refactor`, `sweep`, `experiment`, or `followup`, do not guess the mode — tell the user it is required and ask which one. Requiring the keyword is a safety property, not a formality: `sweep` opens PRs while the user is asleep, so it must never be reached by inference.

**Do not blend attended and unattended policy.** build, refactor, and followup are attended — they pause and ask the user; sweep is unattended — once launched it never asks (its one question, refusing to start without a named area, happens at launch) and records to the morning report instead. Never operate under both policies at once; that blend is the failure this skill guards against. experiment is a third policy of its own, not a blend: attended at the ends (framing, plan approval, report) and autonomous mid-batch strictly under the pre-approved plan and pre-registered decision rules — the approval is its consent boundary, as the named area is sweep's. refactor and followup are the compositions: each *runs on top of* build — read `build.md` (the dev loop) plus your mode's own file (the overrides) — safe because all three are attended. sweep and experiment stand alone; never load either beside another mode. The shared references (`design-taste.md`, `deletion-evidence.md`, `triage.md`) carry mechanisms and evidence standards only, never supervision policy; the mode file owns policy. Read your mode's file(s) now and follow them; they point you to the shared references as needed.

## Review Cycle (all modes)

Define `REVIEW(target, reviewer = codex:codex-rescue)` as:
1) run `reviewer` on `target`.
2) triage each finding against this rubric, and explicitly note what you skip and why:
   - blocker — wrong behavior, data loss, security, race, silently swallowed error: fix always;
   - major — maintainability or missing behavior coverage reaching beyond one local spot: fix this round;
   - minor — local naming, style, or structure: fix only if already touching that code;
   - cosmetic — taste with no behavioral or maintenance consequence: skip and note.
3) repeat from step 1 until a round yields no new actionable findings, or after 3 rounds total. If findings are still unresolved after 3 rounds, surface them and stop retrying: to the user in attended modes, to the morning report in sweep, and in experiment's batch by reverting that leaf uncommitted and carrying the findings into the phase 6 report.

If the default `reviewer` is not available, never degrade to self-review only: in attended modes (build, refactor, followup) abort and ask the user to fix; in sweep abort the run and write the failure to the morning report (Preflight); in experiment abort and ask during the attended phases, and mid-batch stop the batch and write the report from the state so far — a metric alone is not a gate. Substitute another review tool when the user prefers one (e.g. opencode in non-interactive mode or https://github.com/arsenyinfo/nitpicker); in sweep the substitute must be named at launch — never swapped mid-run — and inherits every duty sweep.md assigns to `codex:codex-rescue`: the preflight ping, both gates, and positive confirmation; in experiment the reviewer is fixed no later than plan approval and never swapped mid-batch.

Every `REVIEW` prompt must ask for concrete findings with file/line evidence across these lenses:
- correctness, security, performance, data loss, races, partial failure, and logic consistency;
- scope creep: unrelated changes, hidden behavior changes, or extra features not needed for the task;
- overengineering: pass-through wrappers, factories for one implementation, producer-side interfaces, layer-cake delegation, future-proof hooks, and fallback paths that hide errors (see `references/design-taste.md`);
- tests: missing behavior coverage, untested error paths, fake tests, mocks/monkeypatches of the system under test's own internals, and assertions that pin prose, wording, or generated output rather than behavior;
- project fit: naming, error handling, logging, imports, comments, and structure must match the existing codebase and CLAUDE.md.

Plan/contract reviews additionally check that the contract defines the real problem, has reviewable atomic tasks, names validation commands, avoids compatibility work without a concrete need, and keeps tests tied to behavior rather than implementation wiring.

## Intent contract (all modes)

Before implementing, write an intent contract: **Goal, Inputs/outputs, Acceptance criteria, Scope boundaries, Open questions.** The approver signs off on intent, not on hidden implementation assumptions. Modes scale it:
- **build** saves it to a `/tmp` scratch file and gates it with `REVIEW(plan)`; the trivial fast path may instead state it to the user in a sentence or two.
- **refactor** extends it with a current-state map, target design, and deletion ledger (see `references/refactor.md`).
- **sweep** writes one per cluster and gates it with Codex (see `references/sweep.md`).
- **experiment** writes one per hypothesis-tree leaf — mechanism, expected effect vs the noise floor, pre-registered keep/revert rule, cost envelope (see `references/experiment.md`).
- **followup** seeds it from the ledger entry's evidence and the user's recorded decision (see `references/followup.md`).

## Escalation (all modes)

When implementation proves the approved scope, externally observable behavior, an API/data contract, or the acceptance criteria must change, do not smuggle the change into a local fix. The target of the escalation is the one thing that differs by supervision:
- **build, refactor, followup (attended):** pause and ask the user.
- **sweep (unattended):** the user is asleep — record it under the morning report's *needs-your-call* section with evidence and no code.
- **experiment:** ask the user in the attended phases; mid-batch, an ambiguity takes a best guess disclosed in the report with a rerun offer, while a change to scope, contract, or the frozen protocol parks as a next-batch proposal — never guessed, never applied (see `references/experiment.md`).

## Follow-up ledger (all modes)

A real, verified defect discovered outside the current run's approved scope or blast radius is recorded, never fixed inline (that would be a scope change — Escalation above) and never silently dropped. The ledger lives at a stable per-repo path: `/tmp/tokenmaxxer-followups-<repo-basename>.md` — ephemeral like everything in `/tmp`, an accepted trade; sweep reports and run summaries name the same findings as backup. The path is convention, not memory — after compaction or in a fresh session, `followup` mode re-derives it from the repo alone. Each entry carries:

- one `sweep-key: <normalized-path>:<line-range>:<mechanism-slug>` line — this is the canonical definition of the dedup key format; one name across ledger, reports, and PR bodies so greps match everywhere;
- `file:line` evidence and a one-line defect statement;
- the concrete decision question the user must answer, with a recommended answer — decidable without re-reading the codebase;
- origin (mode, date) and status: `open`, `deferred`, `done (PR)`, or `dropped (reason)`.

Append entries as findings surface, and name the ledger in your final summary whenever you added to it.

Hold your own work to the `REVIEW` lenses above; do not wait for review to catch them. Put temporary files in `/tmp`.
