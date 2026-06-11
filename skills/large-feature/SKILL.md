---
name: large-feature
description: Guidelines on how to work on a large feature or refactoring.
---

You're now entering the serious work mode, that should be done with rigor.

The task: $ARGUMENTS

Our dev loop contains design, implementation and obligatory review.

## Review cycle

Define `REVIEW(target, reviewer = codex:codex-rescue)` as:
1) run `reviewer` on `target`.
2) triage findings by severity: fix correctness and security always; fix maintainability findings that affect more than a single local spot; skip cosmetic nitpicks. Explicitly note what you skip and why.
3) repeat from step 1 until a round yields no new actionable findings, or after 3 rounds total. If findings are still unresolved after 3 rounds, surface them to the user and let them decide.

If the default `reviewer` is not available, abort and ask the user to fix. Substitute another review tool when the user prefers one.

## Design workflow

1) explore the relevant parts of the codebase first. Decompose the exploration into independent angles (e.g. structure, call sites, tests, conventions) and launch one Explore subagent per angle in parallel — a single message with multiple Agent calls — plus codex:codex-rescue for a diverse second perspective. Each subagent reads in its own context, so the raw file dumps stay out of yours; synthesize their reports before planning. Scale the number of angles to the task — a small surface does not need a fleet.
2) map the task to your knowledge, assess whether there are open questions. Ask user if needed, suggest options when possible. Avoid assumptions: back everything with existing code, user's input or web search.
3) based on the knowledge above, draft first version of the plan, save to a scratch file in /tmp.
4) `REVIEW(plan)` to get a second opinion on the plan.
5) once the plan is ready, ask the user to verify the plan. If user has significant feedback, revise and re-run `REVIEW(plan)` at most once before returning to the user.
6) once the plan is approved, start the implementation.

Plan structure:
- The plan should be split into atomic reviewable subtasks, preferably by component.
- Each task should be annotated with [ ] so agent could check in once done.

## Implementation workflow

1) Checkout a new branch from fresh main, unless already on a non-main branch.
2) If the task has isolated components, `REVIEW(component)` each one once it compiles and passes its own tests.
3) After the task is done and reviewed, findings addressed, make a commit, but no push.
4) Run tests, linters, etc before the final review.
5) External gate: `REVIEW(diff)` in the background, where `diff` is the full branch diff against main.
6) Internal gate: `REVIEW(diff, your own subagent with clear context)`. Wait for the external gate (step 5) to finish and merge its findings with this one before proceeding.
7) Push the changes, open a draft PR if not existing yet.
8) Write a summary for the user.

Be sure to check correctness, security, performance, logic consistency, maintainability (no copy paste, no dead code, no unused variables, no redundant code).
Tests exercise real code: mock or monkeypatch only true process boundaries (network, clock, subprocesses, externally-owned storage), never the system under test's own internals — a tmp dir is real I/O and needs no mocking. A test whose setup patches internals is a REVIEW finding; do not downgrade it in triage.
The project favors correctness over robustness. No hidden exceptions, no silent error handling, no magic.
If you need temporary files, place them in /tmp.
