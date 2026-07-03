# build mode

You are in **build** mode: a multi-file feature, cross-cutting refactor, new subsystem, or a root-caused bug fix. The router's Review Cycle, Intent contract, and Escalation rules apply; this file specializes the design and implementation loop.

## Design Workflow

**Planning scales with the change; the external review gate does not.** For a trivial change — single file, no design decisions, obviously-correct intended behavior — skip steps 4–6 (the written plan, `REVIEW(plan)`, and plan approval): state the intent to the user in a sentence or two, then implement. The external `REVIEW(diff)` gate (Implementation Workflow step 6) is mandatory for every change regardless of size and is never skipped; only the internal gate (step 7) may be dropped on this path. If a change you took as trivial grows a design decision or spills past one file, stop and return to full planning.

1) A bug fix is a first-class task here, but triage precedes it — never jump to a fix from the symptom. If the task starts from a bug, failed validation, unexplained behavior, performance regression, flaky test, incident, or uncertain mechanism, invoke `skill: investigate` first and carry its symptom, evidence, mechanism, root cause, and validation recommendation into the plan; the fix targets the established mechanism, not the reported symptom. Only skip triage when the root cause is already proven, not merely suspected.
2) Explore the relevant parts of the codebase first. Decompose the exploration into independent angles (e.g. structure, call sites, tests, conventions) and launch one Explore subagent per angle in parallel, in a single message, plus `codex:codex-rescue` for a diverse second perspective if available (same substitution rule as the Review Cycle). Each subagent reads in its own context, so the raw file dumps stay out of yours; synthesize their reports before planning. Scale the number of angles to the task; a small surface does not need a fleet. If exploration shows the task is actually trivial (single-file, ~tens of lines, no design decisions), say so and take the fast path above — skip planning, keep the diff gate — instead of the full plan/review ceremony.
3) Map the task to your knowledge and assess open questions. Ask the user if needed, suggesting options when possible. Avoid assumptions: back everything with existing code, the user's input, or web search.
4) Draft the plan from that evidence and save it to a scratch file in `/tmp`.
5) Run `REVIEW(plan)`.
6) Ask the user to verify the plan. If the user has significant feedback, revise and re-run `REVIEW(plan)` at most once before returning to the user.
7) Once the plan is approved, start implementation.

Plan structure:
- Start with the intent contract (router's Intent contract section). The user approves intent, not hidden implementation assumptions.
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
6) External gate: run `REVIEW(diff)` in the background, where `diff` is the full branch diff against main. Review adversarially: try to find the strongest reason the change should not ship yet, not reasons it is probably fine. This gate is mandatory for every change, trivial ones included.
7) Internal gate: run `REVIEW(diff, your own subagent with clear context)`. Wait for the external gate to finish and merge its findings with this one before proceeding. Commit fixes from either gate as follow-up commits on the same branch. (Droppable only on the trivial fast path.)
8) Push the changes and open a draft PR if one does not already exist.
9) Write a summary for the user.

## Guardrails

- If implementation proves the approved scope, externally observable behavior, API/data contract, or acceptance criteria must change, escalate per the router's Escalation rule. Do not smuggle contract changes into local fixes.
- A test whose setup patches the system under test's own internals is a `REVIEW` finding; do not downgrade it in triage. Tests exercise real code, mocking only true process boundaries — a tmp dir is real I/O.
- The project favors correctness over robustness. No hidden exceptions, no silent error handling, no magic.
