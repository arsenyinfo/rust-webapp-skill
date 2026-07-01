# Evals and observability

**A harness you cannot observe cannot be improved, and evals are what let you expand autonomy on evidence instead of vibes.** These are the two instruments that turn "the agent seems fine" into a number you can gate on. Without traces you are debugging blind; without evals you are promoting an agent to Level 4 because the demo worked once. Neither is optional before you widen what the agent may do to the world.

**Scale the instrument to the stakes.** For a small or personal harness, the pareto point is a handful of realistic, state-verified cases you re-run by hand plus one trace you can read — not a pass^k dashboard and a held-out test set. The heavier machinery here (pass^k, held-out splits, the full launch gate) earns its cost when a regression moves money, touches many users, or ships unattended. Build up to it; don't front-load it onto an agent that can't do much damage.

## Task-grounded eval sets

Toy prompts measure nothing. "Summarize this paragraph" tells you your model works; it tells you nothing about *your harness* — tool routing, permission gates, error recovery, state transitions. Build a small set (start with 15–40) of **realistic, multi-tool tasks grounded in real systems**: a real (or realistically seeded) database, real tool schemas, real policy rules. Each task should require several tool calls and at least one decision that a naive agent gets wrong — a permission it must ask for, an ambiguous instruction it must narrow, an error it must recover from.

Quality over count. Ten tasks that each exercise a full path through your harness beat a thousand single-turn classification prompts. Annotate each with an author who knows the domain; a task nobody can adjudicate is not an eval, it's noise.

## State-based verification

The reliable way to score an agentic task is to **compare final system state to an annotated goal state**, not to string-match the transcript. After the run, read the database (or filesystem, or ticket status, or mailbox) and assert it equals the goal the task's author recorded. "Did the row get updated to `status=refunded` and a credit of the right amount get written?" is a fact about the world; "did the transcript contain the word 'refunded'?" is a fact about prose, and prose lies.

Substring checks on the transcript are the classic trap: brittle, they pin wording instead of behavior, and they pass agents that *say* the right thing while *doing* the wrong thing (or nothing). Reserve transcript inspection for the few cases where the output *is* the artifact (a drafted message), and even then assert on structured fields, not phrasing. For read-only tasks with no state delta, verify against an expected structured result envelope, not free text.

Author each goal state once, alongside the task. The eval harness sets up the seed state, runs the agent, diffs end-state against goal, and reports pass/fail per task — no human in the loop at scoring time.

## Reliability over average accuracy

Average accuracy (pass^1) hides inconsistency, and inconsistency is what burns you in production: the task that works four times and wipes the wrong record the fifth. Report **pass^k — the probability of solving the *same* task on all k independent trials**, k≥5. A high pass^1 with a low pass^k means your agent is a coin flip wearing a suit.

The τ-bench result is the cautionary tale: even strong function-calling agents (GPT-4o class) are unreliable — under 50% success in the airline domain — and markedly inconsistent everywhere, with pass^8 falling well below pass^1 in retail (roughly a 60% relative drop). Assume your harness is worse until measured. Run each task k times against fixed seed state and report the fraction solved on *every* trial, not on average.

**Hold out a test set.** If you tune tool descriptions, parameter names, and prompt wording against the same tasks you score on, you are overfitting your harness to the eval — the numbers climb while real behavior doesn't. Split: a dev set you iterate against, a test set you look at rarely and never tune to.

## Eval types — small suites, not one giant eval

One monolithic eval tells you *that* something regressed, not *what*. Keep separate, targeted suites so a failure names its own cause:

- **Skill activation** — does the skill fire at the right time, and stay quiet when it shouldn't? Feed both in-scope and adjacent-but-out-of-scope requests.
- **Reference routing** — given a task, does the harness load the *right* reference file, not all of them and not the wrong one?
- **Tool selection** — right tool with valid arguments; forbidden tools not called. Assert on `tool_not_called` as much as `tool_called`.
- **Tool-error recovery** — inject a structured error result; does the agent read it and take the suggested next action, or retry blindly / give up / loop?
- **Permission gates** — on a risky action, does the harness block or ask, rather than execute? This is a harness assertion, not a model one.
- **Scaffold validation** — does generated scaffold/boilerplate pass its own checks (compiles, lints, schema-valid)?
- **Regression** — every production failure becomes a case that must stay fixed. Immutable: don't weaken one to make the suite green.
- **Review agreement** — when independent reviewers (or an LLM judge plus a human sample) grade the same traces, do they converge? Divergence beyond a small margin means the grader is broken, not the agent.

## Instrument alongside accuracy

A pass that took 40 tool calls and $3 is a warning, not a win. Record on every eval run, next to the pass/fail:

- **tool-call count** — sudden growth means the agent is thrashing or the loop lost its footing.
- **tokens** — cost and context-pressure proxy.
- **latency** — wall-clock per task, tail percentiles not just mean.
- **errors** — tool error rate and retry count.

Track these per model and per harness version. A regression that shows up as "same accuracy, double the tool calls" is invisible to a pass-rate-only dashboard and very visible on the bill.

## Minimum trace record

Every run emits one structured trace. If a human cannot read a single trace and reconstruct exactly what happened and why, the trace is incomplete. Record at least:

- **run/trace ID** and a one-line request summary
- **selected skill** and **references loaded**
- **model calls** (model ID on each — model swaps are a top regression source)
- **tool calls** with parameters, secrets redacted (hash or reference large payloads, don't inline them)
- **tool results** (status: success / partial / blocked / failed, plus a result summary)
- **permission decisions** — what rule triggered, who/what approved or denied
- **validation results** — schema checks, scaffold checks, state assertions
- **final outcome**, **errors** (type, recoverable?), **timing**, **token usage**
- **eval labels** when the run is a graded case

The trace is an append-only log: emit an *intent/decision* event (chose a tool, gated an action) the moment the decision is made — before execution — and emit the matching *result/outcome* event once the action returns, so a crash mid-step still leaves the intent recorded even if no result follows. Above all, tag every event with **who decided it**: a *model decision* (chose a tool), a *harness decision* (gated, denied, retried), or a *tool execution* (the side effect itself). Collapsing these three is how you spend an hour blaming the model for a permission the harness denied.

## Replay

A trace you can *replay* is worth far more than one you can only read. Replay re-runs a recorded session against the model to see whether behavior changed — the backbone of regression testing, model-swap evaluation, and debugging a production incident without reproducing its live conditions. It only works if the run was deterministic enough to reconstruct, which is a design constraint, not an afterthought: **freeze the model version** (a silent model swap is a top regression source), **version tool schemas** so a replayed call resolves the same contract, **serialize context deterministically** (stable tool order, stable JSON keys — the cache-aware ordering from context engineering pays off here too), and **feed recorded tool results back instead of re-executing** so a replay never re-fires a real side effect. A harness that can't replay its own traces is one where every regression must be caught live, in production.

## Launch gate

Before you ship a harness *with real blast radius*, or move an agent up a maturity level, the applicable items pass — no exceptions bought with "we'll fix it after launch." A read-only or personal agent needs only the items that bite it (a result envelope, redaction, a readable trace); the full list is for an agent that acts on the world unattended:

- [ ] registry lint passes (tools well-formed, schemas valid)
- [ ] tool-name collision check passes (no `get_file`/`fetch_file`/`download_file` ambiguity)
- [ ] a permission matrix exists (who/what gates which risk classes)
- [ ] a structured result schema exists (every tool returns the envelope, not raw strings)
- [ ] scaffold validation passes (generated boilerplate checks clean)
- [ ] basic evals exist and pass (task-grounded, state-verified, pass^k reported)
- [ ] risky tools have approval gates (draft/commit split where the action is irreversible)
- [ ] logs are redacted (no secrets, tokens, or raw user PII in traces)
- [ ] error results include next actions (never `Error: failed`)
- [ ] a human can read one trace and understand what happened

The last item is the meta-gate: if it fails, you cannot trust that the others were checked honestly.

## Compact eval-case format

Keep cases declarative and readable. Illustrative shape (not a schema to copy verbatim — adapt fields to your harness):

```yaml
- id: refund_within_policy
  task: "Customer asks for a refund on order 4471; it's within the 30-day window."
  expected_behavior:
    - looks up order 4471 before acting
    - asks for approval before issuing the credit
    - issues the refund only after approval
  checks:
    - type: tool_not_called
      tool: delete_order
    - type: final_state
      table: orders
      where: { id: 4471 }
      assert: { status: refunded }
    - type: final_state
      table: ledger
      where: { order_id: 4471 }
      assert: { credit_cents: 2999 }
```

`expected_behavior` is human-readable intent (useful for review-agreement grading); `checks` are machine-run assertions, typed so the harness knows how to evaluate each (`tool_not_called`, `tool_called`, `final_state`, `result_schema`). Score by the checks, run the case k≥5 times, report pass^k.
