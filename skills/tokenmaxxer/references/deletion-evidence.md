# Deletion & dead-code evidence (shared reference)

Used by refactor's deletion ledger and test census, and sweep's stale-workaround, instruction-text, and useless-test lenses. The standard for proving something is safe to delete, or that a workaround's premise has expired. It states mechanisms and evidence only; the mode owns the consequence (approval vs *needs-your-call*).

## What counts as proof of "dead"

Whichever of these apply:

- a callers search from the repository root, covering tests, generated code, and string-name references (DI registries, serialized configs, migrations);
- a config-value search across all environments;
- a test run against the real path;
- git history.

A plausibility argument is not proof.

## Migration-shaped candidates need the history check

For v1/v2 pairs, compatibility shims, never-set config flags, and paths with no callers, the usage search is necessary but not sufficient. Consult `git log`/`git blame`: recent introduction or recent commits touching the item are evidence of an in-flight migration — whose guard looks exactly like dead weight. Treat such items as guards until proven otherwise; items still unclear after the history check become Chesterton's fences.

## "No traffic" / "fully ramped" needs a traffic source

A claim that a superseded path takes no traffic must cite the rollout/config source or a telemetry/log query. A static callers search establishes absence of callers, not absence of traffic.

## Stale-workaround premise proof

Removing a `TODO`/`FIXME`/`HACK`/`XXX` workaround ships only after you prove the premise no longer holds — the newer version exists and resolves the issue, the API is public in the version the project actually uses, the polyfilled feature is available on every supported target. Proof is a concrete check (changelog, release notes, the installed version, a passing test against the real path), not a plausibility argument. A workaround whose removal *is itself* a dependency bump or a behavior change is not a silent cleanup — it escalates per the router's Escalation rule. Only a provably-dead, inert guard is removed as routine cleanup.

## Useless tests

A test earns its keep only by failing when behavior breaks. The useless kinds:

- **tautological** — asserts its own setup: checks a value the test just assigned, or that a mock returns what the mock was configured to return;
- **wiring** — mocks/monkeypatches the system under test's own internals and asserts call sequences, pinning structure instead of behavior;
- **trivial** — asserts constants, getters/setters, or what the type checker already guarantees;
- **prose-pinning** — asserts substrings or snapshots of prose, generated output, or LLM-facing instruction text: pins wording, not behavior, brittle in both directions;
- **duplicate** — coverage another test already provides.

Evidence to delete one: show it cannot fail on a real behavioral break (the check is mutation-shaped — *would this test fail if the behavior it claims to cover were broken?*), or, for a duplicate, cite the surviving test that keeps the coverage. If real behavior might hide beneath the setup, the disposition is *rewrite against real code*, not delete — and a rewrite is a code change owned by the mode's normal workflow, never a silent cleanup.

## Instruction-text split (LLM-facing text)

When the code carries system prompts, tool/skill descriptions, agent instructions, schema `description` fields, or few-shot examples, this text is load-bearing — it steers model behavior, so treat it like code, not comments.

- **Stale reference** — a deletion-only mention of a named referent (a tool, flag, command, or API) that has been *provably removed*. Deletable with the same evidence standard as dead code, and only when the fix is *removing the dead mention*. Do not add a string assertion or snapshot proving the mention is absent — that pins wording, not behavior. If the repo has a real prompt-eval harness, add an eval showing the model no longer names the referent; absent one, it ships on the mode's review gate alone.
- **Semantic edit** — merging drifted guidance into one wording, resolving a contradiction, re-ordering which instruction wins, changing what the model is told. A semantic edit to load-bearing text *is* an observable behavior change: it escalates per the router's Escalation rule, never ships as a silent change — even when one side of it names something old.
- A contradiction you cannot confidently resolve is reported with both competing instructions quoted, no code (a Chesterton's fence).

## Chesterton's fences

Anything that looks dead but cannot be proven dead stays. Never silently delete it. The mode decides the consequence per the router's Escalation rule — always per item, never in bulk.
