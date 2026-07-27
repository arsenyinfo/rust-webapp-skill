# experiment mode

You are in **experiment** mode: metric-driven experimentation toward a stated goal — model quality, latency, cost, prompt or pipeline behavior — where each change is a hypothesis validated by running it, not only by reviewing it. `core.md` owns the Review Cycle, Intent contract, Escalation, and working doc; `triage.md` governs goal framing and any mid-batch investigation; `design-taste.md` governs the code you write.

**A metric is validation, not review** — the ML analog of the test suite, gameable the same way (leakage, eval edits, overfitting to the harness, a win bought with 10× inference cost). The review gates keep their jobs; the metric result is evidence attached to the review, never a bypass of it.

**The autonomous window is phase 5 only** — the router's matrix has the supervision shape. Two mode-local rules govern what may move inside it. An ambiguity (an unspecified parameter, a decision rule the result lands between) is resolved by best guess and disclosed in the report with a rerun offer ("N was unspecified; I tried X — if you prefer Y, the next batch reruns it"). The frozen protocol is the exception: the metric, eval data, validation command, and per-run budget are never best-guessed mid-batch — a change to any of them invalidates every comparison already made, so a hypothesis that needs one is parked as a next-batch proposal.

## Phase 1 — Frame (attended)

1. If the goal or metric is unclear — a symptom-stated goal ("the model feels dumb"), competing candidate metrics, no eval — triage it per `triage.md` before anything else: the "mechanism" to establish is what actually needs to improve and how it will be observed.
2. Fix the **primary metric** and the **secondary metrics** that price a win — inference cost, latency, memory, complexity. A primary-metric gain that regresses a secondary axis is a trade for the user, not a win.
3. Freeze the **protocol**: eval data/split, the exact validation command, and the compute budget per run. This is what phase 5 may never touch.
4. Measure the **noise floor** before any hypothesis spends compute: repeat the unmodified baseline and record the variance — across seeds/runs for stochastic training or eval, repeated post-warmup runs for latency and memory, deterministic accounting for cost. Every keep/revert rule keys off this number; without it, every small delta is an anecdote. If the primary metric admits no meaningful repeat-based floor, stop and settle the protocol with the user before phase 2.
5. Open the working doc (`core.md`) — plan, leaf ledger, follow-ups, and report in one place. If the repo has its own convention for experiment results (an `experiments/` dir, a lab-notebook file), write the results there as well; the working doc stays the run's own record either way.
6. Preflight the repo while still attended: a git repo with a clean worktree (dirty user work is an ask, never a silent stash), the default branch fetched fresh when a remote exists, the run base pinned, and a uniquely named run branch cut from it — phase 5 commits only ever land there.

## Phase 2 — Hypothesis tree

Draft a tree: a few **directions** (distinct mechanisms that could move the metric), each with a few **subideas** (concrete single-change instances). Every leaf is a mini intent contract:

- the mechanism — *why* this change should move the metric, not just what it changes;
- expected effect size relative to the noise floor — an expected effect below it is not runnable as stated;
- the **pre-registered decision rule**: the keep/revert threshold on primary and secondary metrics, written before the run so the number cannot negotiate with you;
- the cost envelope — what secondary-axis spend this gain is allowed;
- the single knob it turns — one mechanism per leaf; a two-knob idea is two leaves or a confounded experiment.

## Phase 3 — Plan gate

Run `REVIEW(tree)` with an extended duty beyond the `core.md` lenses: the reviewer must also **diverge** — propose directions the tree missed — then flag risks (confounds, likely reward-hacking surfaces, eval-validity threats) and recommend a deprioritization. Merge both perspectives into one ranked tree; rank by expected information per unit compute, not by expected win — a cheap experiment that kills a whole direction outranks an expensive incremental gain.

## Phase 4 — User approval (attended)

Present the ranked tree as a table with one fixed column set — every batch, every repo, so approval stays a scan and not a re-orientation:

| rank | leaf | mechanism (one line) | single knob | expected effect vs noise floor | keep/revert rule | cost envelope | reviewer's note |
|---|---|---|---|---|---|---|---|

Alongside it: the frozen protocol, the noise floor, and the proposed **batch budget** (max experiments and wall-clock). The user reorders, prunes, edits rules, and approves. Reordering and pruning need no re-review; an added leaf, a changed decision rule, or a protocol change returns to phase 3 for one more gate round before the batch may start — otherwise the batch would run material the plan gate never saw. The approval is the consent boundary — no batch without it, and the batch never exceeds what it authorizes.

## Phase 5 — Batch execution (autonomous)

Work the ranked tree top-down. Per leaf:

1. Implement the single-knob diff on the run branch (pinned in the phase 1 preflight).
2. **Diff gate** before spending compute: a full `REVIEW(diff)` under all the `core.md` lenses, plus one experiment lens always asked — the confound check: does this diff change exactly what the leaf's contract names and nothing else? A rider change (an extra hyperparameter drift, a "while I'm here" cleanup) poisons the causal claim; strip it or ledger it as its own idea. This is the only full-lens review the leaf's code gets before it can be committed — never narrow it.
3. Run the frozen validation command, repeated when the pre-registered rule needs variance evidence.
4. **Result gate**: `REVIEW(result)` — the reviewer sees the diff, the metric and secondary deltas, and the variance evidence, and tries to refute the causal claim: eval integrity (leakage, harness gaming, test-set peeking), delta vs the noise floor, cost envelope vs the Pareto axes, lucky-seed risk, and whether the observed effect is plausibly produced by the named mechanism.
5. Triage gate findings per the `core.md` rubric, with one experiment-specific scoping: a leaf diff is by definition code you are touching, so the minor tier's "if already touching" condition always holds — read it as *fix inline without spending a review round*, and cosmetic as note-and-proceed; otherwise every naming nit would be commit-blocking and could burn the round cap. A blocker or major from either gate blocks the commit regardless of the metric: fix and re-run that gate within the `core.md` 3-round cap, else revert the leaf and carry the unresolved findings into the report. Only then apply the leaf's pre-registered rule: **keep** → commit on the run branch; **revert** → discard the diff. Either way, append the leaf's ledger entry to the working doc's Progress section: hypothesis, decision, deltas, and the *reason* — "refuted: below noise floor" teaches the next batch; a bare number does not.

Comparison discipline: leaves run sequentially on the run branch, so each leaf's measured delta is *marginal* — taken against the branch tip, earlier kept commits included — and the pre-registered rule applies to that marginal delta. Record both it and the cumulative delta against the phase-1 baseline in the ledger. A leaf whose contract requires isolation from earlier keeps runs from the run base in a separate worktree instead, noted in the ledger.

Tree discipline: evidence may **prune and reorder within the approved tree** — a refuted direction's remaining subideas are skipped (ledgered as `skipped: direction refuted by <leaf>`), a promising sibling may be promoted — but only among approved leaves. New ideas discovered mid-batch are recorded as next-batch proposals, never run. The batch ends when the tree or the budget is exhausted.

Boundaries, restated once: protocol changes park as next-batch proposals (never best-guessed); ambiguities take a disclosed best guess; code defects discovered along the way become follow-up blocks in the working doc under `core.md`'s admission rules — `kind: defect` at blocker/major only, `kind: consent` at any tier — never fixed inline. If the reviewer becomes unavailable mid-batch, stop the batch and write the report from the state so far — a metric alone is not a gate.

## Phase 6 — Report (attended)

Deliver, in the working doc's Outcome section and summarized to the user:

1. A results table covering every leaf, with one fixed column set so batches stay comparable and greppable across runs:

   | leaf | decision (kept / refuted / skipped) | marginal Δ | cumulative Δ | secondary-axis cost | reason (one line) |
   |---|---|---|---|---|---|
2. What the batch *taught*: mechanism-level conclusions ("attention-side changes are all below noise at this scale"), not just numbers.
3. Every best guess taken, with its rerun offer, and every parked protocol-change proposal.
4. Every follow-up block added during the batch — `sweep-key`, kind, tier, evidence, decision question — and the working doc's path, so `followup` can be pointed at it.
5. The **next-batch proposal**: a ranked tree seeded from surviving subideas, mid-batch discoveries, parked proposals, and rerun offers — phase 2 of the next cycle, pre-built. Approving it starts the cycle again; kept commits ride the run branch, and shipping it (draft PR or merge) is the user's call at this point.
