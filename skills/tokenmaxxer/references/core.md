# Core machinery (all modes)

The review gates, intent contract, escalation mechanism, and working doc every mode shares. The router's supervision matrix decides *who approves* and *where escalations go*; this file is *how* each mechanism works.

## Review Cycle

Define `REVIEW(target, reviewer = codex:codex-rescue)` as:

1. run `reviewer` on `target`.
2. triage each finding against this rubric, and explicitly note what you skip and why:
   - **blocker** — wrong behavior, data loss, security, race, silently swallowed error: fix always;
   - **major** — maintainability or missing behavior coverage reaching beyond one local spot: fix this round;
   - **minor** — local naming, style, or structure: fix only if already touching that code;
   - **cosmetic** — taste with no behavioral or maintenance consequence: skip and note.
3. repeat from step 1 until a round yields no new actionable findings, or after 3 rounds total. If findings are still unresolved after 3 rounds, surface them and stop retrying — to the user in attended modes, to the run doc in sweep, and in experiment by reverting that leaf uncommitted and carrying the findings into the phase 6 report.

**Never degrade to self-review only.** If the reviewer is unavailable:

| mode | behavior |
|---|---|
| build, refactor, followup | abort; ask the user to fix it |
| sweep | abort the run; write the failure to the run doc (Preflight) |
| experiment | attended phases: abort and ask · mid-batch: stop the batch and report from the state so far — a metric alone is not a gate |

Substitute another review tool when the user prefers one (e.g. opencode in non-interactive mode, or https://github.com/arsenyinfo/nitpicker). In `sweep` the substitute must be named at launch — never swapped mid-run — and inherits every duty `sweep.md` assigns to `codex:codex-rescue`: the preflight ping, both gates, and positive confirmation. In `experiment` the reviewer is fixed no later than plan approval and never swapped mid-batch.

Every `REVIEW` prompt must ask for concrete findings with file/line evidence across these lenses:

- correctness, security, performance, data loss, races, partial failure, and logic consistency;
- scope creep: unrelated changes, hidden behavior changes, or extra features not needed for the task;
- overengineering: pass-through wrappers, factories for one implementation, producer-side interfaces, layer-cake delegation, future-proof hooks, and fallback paths that hide errors (see `design-taste.md`);
- tests: missing behavior coverage, untested error paths, fake tests, mocks/monkeypatches of the system under test's own internals, and assertions that pin prose, wording, or generated output rather than behavior;
- project fit: naming, error handling, logging, imports, comments, and structure must match the existing codebase and CLAUDE.md.

Plan and contract reviews additionally check that the contract defines the real problem, has reviewable atomic tasks, names validation commands, avoids compatibility work without a concrete need, and keeps tests tied to behavior rather than implementation wiring.

## Intent contract

Before implementing, write an intent contract into the working doc: **Goal, Inputs/outputs, Acceptance criteria, Scope boundaries, Open questions.** The approver signs off on intent, not on hidden implementation assumptions. Modes scale it:

| mode | contract shape |
|---|---|
| build | one per task, gated by `REVIEW(plan)`; the trivial fast path may instead state it to the user in a sentence or two |
| refactor | build's, plus a current-state map, target design, and deletion ledger (`refactor.md`) |
| sweep | one per cluster, gated by the Codex plan gate (`sweep.md`) |
| experiment | one per hypothesis-tree leaf: mechanism, single knob turned, expected effect vs the noise floor, pre-registered keep/revert rule, cost envelope (`experiment.md`) |
| followup | seeded from the follow-up block's evidence and the user's recorded decision (`followup.md`) |

## Escalation

When implementation proves the approved scope, externally observable behavior, an API or data contract, or the acceptance criteria must change, do not smuggle the change into a local fix. Stop and route it — the router's supervision matrix names the target for your mode.

## Working doc

One doc per run, at `/tmp/tokenmaxxer-<repo-basename>-<mode>-<slug>-<YYYYMMDD-HHMM>.md`. The timestamp is not decoration: without it a repeated `sweep <same-area>` overwrites the earlier run's undrained findings. Never reuse or overwrite an existing doc — if the name is already taken (two runs inside the same minute), append `-2`, `-3`, … until it is free. It is the run's only durable artifact, so a compacted or resumed session re-derives its state from it rather than from memory. Append as the run proceeds — never save it up for the end, so a run killed midway still leaves a readable partial.

```
# <mode> run — <slug>
run base: <sha> · started: <date> · scope: <area or component>

## Intent contract
## Progress          — plan tasks, cluster ledger, or leaf ledger, per the mode
## Follow-ups        — blocks, below
## Outcome           — summary, PRs opened, anything incomplete
```

### Follow-up blocks

Recorded here, never fixed inline (that is a scope change — Escalation above) and never silently dropped: a verified defect outside the run's approved scope or blast radius, anything the mode reserves for the user's judgment (sweep's *needs-your-call* — `sweep.md` owns the criteria), and any finishable operational leftover. There is no admission gate — an item that earned a decision question earns a block; `tier` orders the reading, it never decides what is recorded.

```
- sweep-key: <normalized-path>:<line-range>:<mechanism-slug>
  tier: blocker | major | minor
  subsystem: <name>
  defect: <one line>, with (<file:line>) when it has a code location
  question: <the decision the user must answer, with a recommended answer>
  status: open | deferred | declined (<reason>) | done (<PR, or the step that was completed>)
```

`sweep-key` is the canonical dedup key across run docs, commit messages, and PR bodies — one name so a single grep matches everywhere (it predates the other modes; the name stays because open draft PRs already carry it). An operational leftover has no code location: key it as `branch/<branch-name>:-:<mechanism-slug>` so the shape stays greppable and one branch's leftover dedups against itself. `question` must be decidable without re-reading the codebase.

Cross-run memory is deliberately best-effort: the `sweep-key` lines in **open draft-PR bodies** are the only durable record, and prior run docs survive in `/tmp` only until it clears. A finding declined in one run may resurface in a later one — an accepted trade for having no shared queue that accumulates across sessions.

---

Hold your own work to the `REVIEW` lenses above; do not wait for review to catch them. Put temporary files in `/tmp`.
