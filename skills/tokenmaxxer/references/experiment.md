# experiment mode — metric-driven batches

You are in **experiment** mode: each change is a hypothesis validated by running it, toward a stated goal — model quality, latency, cost, prompt or pipeline behavior. **A metric is validation, not review** — it is gameable exactly like a test suite (leakage, eval edits, a win bought with 10× inference cost), so the review gates keep their jobs and the metric result is evidence inside them, never a bypass. Attended at the ends; autonomous only mid-batch, strictly under the approved tree.

## Frame (attended)

1. An unclear goal or metric ("the model feels dumb") gets the triage ladder (SKILL.md) first: what actually needs to improve and how it will be observed.
2. Fix the **primary metric** and the **secondary metrics** that price a win — cost, latency, memory, complexity. A primary gain that regresses a secondary axis is a trade for the user, not a win.
3. **Freeze the protocol**: eval data/split, the exact validation command, the per-run compute budget. The batch may never touch these — a change to any invalidates every comparison already made.
4. **Measure the noise floor** before any hypothesis spends compute: repeat the unmodified baseline and record the variance. Every keep/revert rule keys off it; without it every small delta is an anecdote. No meaningful floor → settle the protocol with the user before proceeding.
5. Open the working doc; mirror results into the repo's own convention (`experiments/`, a lab notebook) when one exists. Preflight while attended: clean tree (dirty user work is an ask, never a silent stash), default branch fetched fresh, run base pinned, a uniquely named run branch cut from it — batch commits land only there.

## Tree (attended)

Draft a few **directions** (distinct mechanisms that could move the metric), each with concrete single-change **leaves**. Every leaf is a mini contract: the mechanism (*why* it moves the metric, not just what changes), expected effect vs the noise floor (below the floor → not runnable as stated), the **pre-registered keep/revert rule** written before the run so the number cannot negotiate with you, the cost envelope, and the single knob it turns — a two-knob idea is two leaves or a confounded experiment.

**REVIEW(tree)** with one extra duty: the reviewer must also *diverge* — propose directions the tree missed — then flag confounds, reward-hacking surfaces, and eval-validity threats. Rank by expected information per unit compute: a cheap experiment that kills a whole direction outranks an expensive incremental gain.

**Approval.** Present the ranked tree as a table with a fixed column set — rank | leaf | mechanism | knob | expected effect vs floor | keep/revert rule | cost envelope | reviewer's note — plus the frozen protocol, the noise floor, and the batch budget (max experiments, wall-clock). The user reorders, prunes, edits, approves. An added leaf, a changed rule, or a protocol change goes back through the gate first. The approval is the consent boundary; the batch never exceeds it.

## Batch (autonomous)

Work the ranked tree top-down, leaves sequential on the run branch. Per leaf:

1. Implement the single-knob diff.
2. **REVIEW(diff)** before spending compute — full SKILL.md lenses plus the confound check: does this diff change exactly what the leaf's contract names and nothing else? A rider change (a hyperparameter drift, a "while I'm here" cleanup) poisons the causal claim — strip it or ledger it as its own idea.
3. Run the frozen validation command, repeated when the rule needs variance evidence.
4. **REVIEW(result)**: the reviewer sees the diff, the metric and secondary deltas, and the variance, and tries to refute the causal claim — leakage, harness gaming, delta vs the noise floor, cost vs the envelope, lucky-seed risk, whether the named mechanism plausibly produced the effect.
5. A blocker or major from either gate blocks the commit regardless of the metric — fix and re-gate within the round cap (SKILL.md), else revert the leaf and carry the findings into the report. (Minors: fix inline without a review round; cosmetics: note and proceed.) Only then apply the pre-registered rule: **keep** → commit; **revert** → discard. Either way ledger the leaf: hypothesis, decision, **marginal Δ** (vs the branch tip — what the rule judges), **cumulative Δ** (vs the phase-1 baseline), secondary-axis cost, and the reason — "refuted: below noise floor" teaches the next batch; a bare number does not. A leaf whose contract requires isolation from earlier keeps runs from the run base in a separate worktree, noted in the ledger.

Mid-batch boundaries: evidence may prune and reorder **within** the approved tree (a refuted direction's remaining leaves are skipped, ledgered as `skipped: direction refuted by <leaf>`); new ideas are next-batch proposals, never run. An ambiguity takes a disclosed best guess with a rerun offer. A protocol or scope change parks as a proposal. Code defects found along the way follow the SKILL.md follow-up admission test. Reviewer unavailable → stop the batch and report from the state so far.

## Report (attended)

Deliver in the working doc's Outcome and summarized to the user: the results table with fixed columns (leaf | decision | marginal Δ | cumulative Δ | secondary-axis cost | reason); what the batch *taught* at mechanism level ("attention-side changes are all below noise at this scale"), not just numbers; every best guess with its rerun offer and every parked proposal; any admitted follow-up blocks; and the **next-batch proposal** — a ranked tree seeded from survivors, discoveries, and parked items, so approving it starts the next cycle. Shipping the run branch (draft PR or merge) is the user's call.
