---
name: tokenmaxxer
description: Serious engineering work with a reviewed plan and adversarial review gates. Pick a mode with the first word of the argument. `build` — a multi-file feature, a root-caused bug fix, or a broad cross-cutting change; skips planning for trivial one-file changes but always keeps the diff-review gate. `refactor` — consolidate a component that grew by accretion into one coherent design, behavior-preserving, attended. `sweep` — an unattended overnight housekeeping run over a named area that ships tiny verified fixes as subsystem draft PRs. Invoke explicitly, e.g. `/tokenmaxxer refactor <component>`.
argument-hint: "build <task>  |  refactor <component>  |  sweep <area>"
compatibility: "requires an external review tool (e.g. codex:codex-rescue or opencode) and the investigate skill; all modes use the design-taste reference, refactor/sweep add deletion-evidence; sweep additionally needs the gh CLI and a git repo with a remote"
---

Serious work mode. Task: $ARGUMENTS

The dev loop is the same across modes: understand the problem, capture intent in a contract, implement in reviewable slices, validate, and run adversarial review gates. What differs is *who approves*, *what is allowed to change*, and *how work is chunked* — that lives in the mode file.

## Mode dispatch

The first word of `$ARGUMENTS` names the mode and is **required — there is no default**. It is always a mode selector, never part of the task, so a task that happens to start with the word "refactor" or "sweep" is never misread.

- **`build <task>`** → `references/build.md`. A feature, a root-caused bug fix, or a broad cross-cutting change — a codebase-wide refactor-shaped change (a rename, a pattern migration) included.
- **`refactor <component>`** → `references/refactor.md`. Consolidate a component that grew by accretion into one coherent design; behavior-preserving. One component — codebase-wide is `build`.
- **`sweep <area>`** → `references/sweep.md`. Unattended overnight cleanup of a named area, shipping tiny verified fixes as draft PRs.

If the first word is not exactly one of `build`, `refactor`, or `sweep`, do not guess the mode — tell the user it is required and ask which one. Requiring the keyword is a safety property, not a formality: `sweep` opens PRs while the user is asleep, so it must never be reached by inference.

**Do not blend attended and unattended policy.** build and refactor are attended — they pause and ask the user; sweep is unattended — once launched it never asks (its one question, refusing to start without a named area, happens at launch) and records to the morning report instead. Never operate under both policies at once; that blend is the failure this skill guards against. refactor is the one composition: it *runs on top of* build — read both `build.md` (the dev loop) and `refactor.md` (the overrides), which is safe because both are attended. sweep stands alone; never load it beside build or refactor. The shared references (`design-taste.md`, `deletion-evidence.md`) carry mechanisms and evidence standards only, never supervision policy; the mode file owns policy. Read your mode's file(s) now and follow them; they point you to the shared references as needed.

## Review Cycle (all modes)

Define `REVIEW(target, reviewer = codex:codex-rescue)` as:
1) run `reviewer` on `target`.
2) triage each finding against this rubric, and explicitly note what you skip and why:
   - blocker — wrong behavior, data loss, security, race, silently swallowed error: fix always;
   - major — maintainability or missing behavior coverage reaching beyond one local spot: fix this round;
   - minor — local naming, style, or structure: fix only if already touching that code;
   - cosmetic — taste with no behavioral or maintenance consequence: skip and note.
3) repeat from step 1 until a round yields no new actionable findings, or after 3 rounds total. If findings are still unresolved after 3 rounds, surface them to the user (or, in sweep, to the morning report) and stop retrying.

If the default `reviewer` is not available, never degrade to self-review only: in attended modes (build, refactor) abort and ask the user to fix; in sweep abort the run and write the failure to the morning report (Preflight). Substitute another review tool when the user prefers one (e.g. opencode in non-interactive mode or https://github.com/arsenyinfo/nitpicker); in sweep the substitute must be named at launch — never swapped mid-run — and inherits every duty sweep.md assigns to `codex:codex-rescue`: the preflight ping, both gates, and positive confirmation.

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

## Escalation (all modes)

When implementation proves the approved scope, externally observable behavior, an API/data contract, or the acceptance criteria must change, do not smuggle the change into a local fix. The target of the escalation is the one thing that differs by supervision:
- **build, refactor (attended):** pause and ask the user.
- **sweep (unattended):** the user is asleep — record it under the morning report's *needs-your-call* section with evidence and no code.

Hold your own work to the `REVIEW` lenses above; do not wait for review to catch them. Put temporary files in `/tmp`.
