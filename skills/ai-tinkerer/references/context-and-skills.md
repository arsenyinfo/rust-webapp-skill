# Context and skills

Context is a finite resource. Every token you spend on capability the model doesn't need this turn is a token stolen from the working set — and from cache hits. The job is to find the smallest set of high-signal tokens that maximizes the desired outcome. Skills and progressive disclosure are how you buy capability without paying for it up front; context engineering and memory are how you keep the working set lean across a long run.

## Progressive disclosure — the scaling principle

A skill reveals detail in three levels, and each level you *don't* trigger costs you nothing:

1. **Metadata — `name` + `description`, always pre-loaded.** This is the only part that lives in the system prompt for every session, whether or not the skill fires. Budget it like it's expensive, because at scale it is: ~80 tokens per skill (measured median across a set of production skills; a whole library of ~17 ran ~1,700 tokens combined). Keep it tight. A hundred skills at 80 tokens is 8k tokens of always-on tax before the agent has done anything.
2. **`SKILL.md` body — read on trigger.** Loaded only when the description matches the task. Keep it under ~500 lines / ~5000 tokens. The body is a *router and operating manual*, not a manual dump: state the workflow, point to references, stop. If it's creeping past 500 lines, you're putting reference depth in the body.
3. **Bundled references and scripts — read/executed on demand.** A reference file enters context only when the body sends the agent to it. A script's *output* enters context; its **code never does** — the agent runs `scaffold_project webapp`, sees the result, and pays zero tokens for the 300 lines that produced it. This is the whole trick: deterministic work priced at output size, not source size.

The discipline is the same at every layer of the harness — tool surfaces, connectors, skills. Front-load nothing you can defer.

## The description is the trigger — and the single most important field

The metadata description decides whether the skill fires at all. A perfect body no agent loads is dead weight. Write it to two requirements:

- **What it does AND when to use it.** Third person, concrete trigger terms the agent will actually see in a request. "Use when building or reviewing an agent runtime, a set of agent-facing tools, an MCP server, an approval flow…" beats "helps with agents."
- **Slightly pushy.** Agents systematically *under*-trigger skills — they'd rather wing it than load help. Counter that bias deliberately: name the triggering nouns, and say "even when the request says 'add a tool' without naming a harness." Push toward firing, not away.

Reject vague names (`helper`, `utils`, `tools`, `assistant`) and generic ones (`data`, `files`, `documents`) — they trigger on everything and nothing. Prefer a **gerund or verb-led** name, lowercase-hyphen, ≤64 chars: `processing-pdfs`, `reviewing-diffs`, `scaffolding-webapps`. The name is a promise about *what the skill acts on*.

## Match freedom to fragility (H / M / L)

Tag every instruction you write with how much latitude it grants, and match the tag to how fragile the operation is:

| Freedom | Form | Use when |
|---|---|---|
| **High** | Prose, "figure it out" | Many paths are valid; judgment is the point. Over-constraining here just makes the agent brittle to input variation. |
| **Medium** | Parameterized script, a preferred pattern named | One way is better but not the only way. Give the default, allow deviation. |
| **Low** | Exact script, few params, verbatim sequence | The operation is fragile, consistency is critical, or a specific order must hold. Prescribe it and treat variation as a defect. |

The two failure modes are symmetric: locking down a judgment call (over-constraint → brittleness) and leaving a fragile op open (under-constraint → the agent improvises and breaks it). Annotate rules so a reviewer can see at a glance which you've done.

## Code as tool AND documentation

A bundled script serves two roles, and you must say which one applies. State explicitly whether the agent should **RUN** it (execute, consume output) or **READ** it (a worked reference to imitate). Ambiguity here wastes tokens — the agent reads a script it should have run, or runs one meant as an example.

Rule of thumb: **bundle a script for anything rewritten more than once.** If the agent regenerates the same boilerplate, the same validation, the same transform across runs, that's not judgment — it's a deterministic operation masquerading as one. A `scaffold_project(type)` that emits correct, validated structure beats 500 words describing that structure: it's cheaper (output-priced, not prose-priced) and it can't drift.

## Keep skills lean — the bloat trap

The cautionary tale is a widely-used *skill-creator* meta-skill whose body ballooned to ~8000 tokens — the largest in its library against a median near 2000 — until reviewers noted it "reads more like developer documentation than an operational skill," violating the very lean-and-imperative principles it exists to teach. The lesson: **even meta-skills stay lean.** The body is an operating manual, not a knowledge base. When you feel the urge to explain everything, that's the signal to move depth into a reference and leave a pointer.

Two specific bloat sources to resist:
- **Oppressive MUSTs.** A wall of imperatives reads as noise; the agent can't tell the load-bearing rule from the nervous one. Reserve strong language for the few rules that are actually load-bearing.
- **Fiddly overfit rules.** Every rule bolted on to prevent one observed failure is an over-fit that makes the skill fragile to the next variation. When the agent fails the same way twice, the fix is usually a validator, a tool, or a schema constraint — deterministic — not one more line of prose.

## Context engineering

Context is a budget, not a bucket. Two levers keep it lean:

- **Just-in-time retrieval.** Don't stuff everything up front on the theory it might be needed. Pull on demand: `glob`/`grep`/`head`/`tail` to fetch the relevant slice when the task reaches it. Attach summaries and reference cards, not whole files — if two paragraphs of a 10k-token doc matter, attach the two paragraphs with a citation. Anticipate the next step and fetch for it; don't dump the world in case.
- **Cache-aware ordering.** Providers cache prompt *prefixes*. Put stable content first so the prefix stays cacheable across turns: tool definitions in a deterministic order, static instructions, the skill index. Put volatile content last: timestamps, request IDs, fresh tool results, retrieved content. A timestamp or session UUID at the *start* of the prompt invalidates the cache every single turn — a pure, recurring tax. Serialize deterministically: stable tool order, stable JSON key order, so identical state produces an identical prefix.

## Memory and compaction

A long run overflows the window; compaction is inevitable. What matters is *what survives it*.

- **Auto-compaction preserves working state, discards conversational prose.** Keep: approval state, the active plan, loaded rules and constraints, changed artifacts, key facts/decisions/blockers. Drop: pleasantries, redundant tool results, resolved sub-tasks, duplicate search results. The classic compaction bug is summarizing away the fact that a destructive action was already approved, or which plan step is active — state the agent then can't reconstruct.
- **Durable knowledge lives in artifacts, not only chat.** Anything the agent must not forget belongs in an agent-readable source-of-truth file (a plan file, a decisions log, a scratch contract), not solely in conversation history that compaction can erase. Preserve working state as *structured data*, not paragraphs — it survives compaction better and the model scans it faster.
- **Handoff / rehydration summaries carry state across sessions.** When an agent hands off or a session resumes, don't replay the transcript — emit a compact summary (task, accomplished, decisions with rationale, remaining work, active plan, changed files, blockers, next action) and rehydrate from *that* plus the changed artifacts. The resumed session starts fresh with a state snapshot, not the token cost of the whole prior run.
