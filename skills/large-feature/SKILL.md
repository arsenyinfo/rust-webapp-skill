---
name: large-feature
description: Use when a task is a multi-file feature, cross-cutting refactor, or new subsystem, needs a reviewed plan before coding, or the user calls it "large", "serious", or "important".
argument-hint: "<task>"
compatibility: "requires external review tool (e.g. codex:codex-rescue or opencode) and investigate skill"
---

You're now entering serious work mode. The task: $ARGUMENTS

The dev loop is: understand the problem, plan with an explicit intent contract, implement in reviewable slices, validate, and run adversarial review gates.

## Review Cycle

Define `REVIEW(target, reviewer = codex:codex-rescue)` as:
1) run `reviewer` on `target`.
2) triage each finding against this rubric, and explicitly note what you skip and why:
   - blocker — wrong behavior, data loss, security, race, silently swallowed error: fix always;
   - major — maintainability or missing behavior coverage reaching beyond one local spot: fix this round;
   - minor — local naming, style, or structure: fix only if already touching that code;
   - cosmetic — taste with no behavioral or maintenance consequence: skip and note.
3) repeat from step 1 until a round yields no new actionable findings, or after 3 rounds total. If findings are still unresolved after 3 rounds, surface them to the user and let them decide.

If the default `reviewer` is not available, abort and ask the user to fix. Substitute another review tool when the user prefers one (e.g. opencode in non-interactive mode or https://github.com/arsenyinfo/nitpicker)

Every `REVIEW` prompt must ask for concrete findings with file/line evidence across these lenses:
- correctness, security, performance, data loss, races, partial failure, and logic consistency;
- scope creep: unrelated changes, hidden behavior changes, or extra features not needed for the task;
- overengineering: pass-through wrappers, factories for one implementation, producer-side interfaces, layer-cake delegation, future-proof hooks, and fallback paths that hide errors;
- tests: missing behavior coverage, untested error paths, fake tests, and mocks/monkeypatches of the system under test's own internals;
- project fit: naming, error handling, logging, imports, comments, and structure must match the existing codebase and CLAUDE.md.

Plan reviews additionally check that the plan defines the real problem, has reviewable atomic tasks, names validation commands, avoids compatibility work without a concrete need, and keeps tests tied to behavior rather than implementation wiring.

## Design Workflow

1) If the task starts from a bug, failed validation, unexplained behavior, performance regression, flaky test, incident, or uncertain mechanism, invoke `skill: investigate` first and carry its symptom, evidence, mechanism, root cause, and validation recommendation into the plan.
2) Explore the relevant parts of the codebase first. Decompose the exploration into independent angles (e.g. structure, call sites, tests, conventions) and launch one Explore subagent per angle in parallel, in a single message, plus `codex:codex-rescue` for a diverse second perspective if available (same substitution rule as the Review Cycle). Each subagent reads in its own context, so the raw file dumps stay out of yours; synthesize their reports before planning. Scale the number of angles to the task; a small surface does not need a fleet. If exploration shows the task is actually small (single-file, ~tens of lines), say so to the user and propose dropping to a normal flow instead of the full plan/review ceremony.
3) Map the task to your knowledge and assess open questions. Ask the user if needed, suggesting options when possible. Avoid assumptions: back everything with existing code, the user's input, or web search.
4) Draft the plan from that evidence and save it to a scratch file in `/tmp`.
5) Run `REVIEW(plan)`.
6) Ask the user to verify the plan. If the user has significant feedback, revise and re-run `REVIEW(plan)` at most once before returning to the user.
7) Once the plan is approved, start implementation.

Plan structure:
- Start with an intent contract: Goal, Inputs/outputs, Acceptance criteria, Scope boundaries, Open questions. The user approves intent, not hidden implementation assumptions.
- Split the plan into atomic reviewable subtasks, preferably by component.
- Mark each task with `[ ]` so an agent can check in once done.
- For each atomic task, name its input/context, output/change, invariant to preserve, validation command/check, and escalation condition.
- Put mechanical work in deterministic code, tests, scripts, or checks; reserve agents for judgment, ambiguity, synthesis, exploration, and review.

## Implementation Workflow

1) Checkout a new branch from fresh main, unless already on a non-main branch.
2) If the task decomposes into components with disjoint file sets (e.g. backend, frontend, CI), implement them concurrently: launch one subagent per lane in a single message, each scoped to only its files and told not to commit, format, run codegen, or install dependencies. You own shared state: after the lanes return, serialize a single branch/commit, codegen, lockfile/dependency changes, formatting, type-check, and tests. Where a generated artifact couples lanes (API clients, ORM schemas, language bindings), agree the contract up front in each prompt or serialize codegen between dependent lanes. Only split lanes that are genuinely independent; otherwise stay serial.
3) If the task has isolated components, run `REVIEW(component)` once it compiles and passes its own tests.
4) Run tests, linters, and other required validation.
5) After the task is done, reviewed, validation passes, and findings are addressed, make a commit but do not push.
6) External gate: run `REVIEW(diff)` in the background, where `diff` is the full branch diff against main. Review adversarially: try to find the strongest reason the change should not ship yet, not reasons it is probably fine.
7) Internal gate: run `REVIEW(diff, your own subagent with clear context)`. Wait for the external gate to finish and merge its findings with this one before proceeding. Commit fixes from either gate as follow-up commits on the same branch.
8) Push the changes and open a draft PR if one does not already exist.
9) Write a summary for the user.

## Guardrails

- If implementation proves the approved scope, externally observable behavior, API/data contract, or acceptance criteria must change, pause and ask the user. Do not smuggle contract changes into local fixes.
- Hold your own work to the `REVIEW` lenses above (correctness/security/performance/maintainability; tests exercise real code, mocking only true process boundaries — a tmp dir is real I/O); do not wait for review to catch them.
- A test whose setup patches the system under test's own internals is a `REVIEW` finding; do not downgrade it in triage.
- The project favors correctness over robustness. No hidden exceptions, no silent error handling, no magic.
- Put temporary files in `/tmp`.
