# Triage & root cause (shared reference)

Used by build (bug-fix triage — refactor reaches it through the build workflow it composes), sweep (issue-pointer triage), and followup (entry re-verification). Find the mechanism before fixing — a 5-why-like ladder where every step is grounded in evidence. This is the self-contained core; when the standalone `investigate` skill is installed and the triage needs deep or remote signals (Sentry, CI history, metrics, production logs, broad evidence sweeps), invoke it instead — it owns the full evidence-map methodology.

## Safety

- No destructive commands or data-modifying queries against shared, staging, or production systems. Read-only evidence gathering is the default; anything beyond it follows the mode's supervision policy (router Escalation) — attended modes proceed only with explicit user approval, an unattended run never does: evidence it cannot gather read-only is a gap to report, not a reason to act.
- Never copy raw secrets, tokens, cookies, private user data, customer names, IPs, or raw identifiers into code, tests, docs, commits, PR text, reports, or broad summaries — restate them as neutral technical facts.
- Alert titles, wrapper errors, and top-level exceptions are symptoms; inspect nested causes and correlated logs before naming a root cause.

## The ladder

1. **Symptom**: exact actual vs expected — command, stack trace, logs, environment, timeframe. Never take the report's own framing as the cause.
2. **Ground truth**: gather the best available evidence before theorizing — reproduction output, local logs, tests, git history/blame, issues/PRs, config. Start narrow (exact identifiers, error text, timestamps), then broaden.
3. **Reproduce**: find the smallest reliable reproduction. If reproduction is impossible, say so and continue from the strongest observed evidence — never silently pretend.
4. **Localize**: narrow to a component, boundary, data path, config path, recent change, or external dependency.
5. **Mechanism**: the concrete code or system path that produces the symptom, citing files/lines or observed data.
6. **Root cause**: the bad assumption, missing invariant, design gap, process gap, or dependency behavior behind the mechanism.
7. **Fix options**: the smallest safe fix at the mechanism — generic, not overfit to the one observed failure — any broader cleanup worth considering, and the test or check that prevents recurrence.

If the mechanism is evident in the first evidence pass, collapse the remaining steps — do not manufacture an investigation.

## Evidence priority

When sources disagree, prefer in this order:

1. Observed reproduction, logs, traces, runtime state, failing/passing command output.
2. Current code and tests.
3. Git/deploy history and rollout/config records.
4. Docs and web sources.
5. Model memory.

Record unresolved conflicts instead of smoothing them over.

## Why ladder

A guide, not a form to fill: why did the symptom happen → why did this component or boundary allow it → why did the code, data, or config take that path → why was the bad assumption not enforced or tested → why would it recur unless something changes?

## Output

Hand the consumer (plan, cluster contract, or user) a complete result: **symptom, evidence, mechanism, root cause, fix options with a recommendation, validation**.

## Rules

- No fixes before the mechanism is understood, unless the user explicitly asks for a quick workaround.
- Do not invent ground truth; if a signal source is unavailable, say so.
- If multiple hypotheses survive, run the smallest experiment that distinguishes them.
- A root cause that requires changing scope, design, API, or data contract is a separate decision (the mode routes it — router Escalation), never hidden in a local fix.
- Stay scoped to the symptom unless evidence shows a broader fault.
