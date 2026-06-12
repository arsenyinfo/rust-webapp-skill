---
name: unify
description: Refactor a component that grew by accretion (layered wrappers, parallel v1/v2 paths, stale tests, dead abstractions, outdated comments) into one coherent design. 
argument-hint: "<component name or path>"
compatibility: "requires external review tool (e.g. codex:codex-rescue or opencode) and large-feature skill"
---

You are unifying a component that grew by additive layers rather than coherent design. Target component: $ARGUMENTS

This skill inherits the large-feature workflow by composition. As your FIRST action, invoke the Skill tool with `skill: large-feature` and args:

> Unify the component `$ARGUMENTS`: refactor it from accreted layers into one coherent design.

The injected large-feature workflow (review cycle, design workflow, implementation workflow) governs the dev loop. The sections below specialize its phases for layered-code refactoring; where they conflict, the rules here win.

**Hard default — behavior preservation.** /unify must not change externally observable behavior: API responses, CLI output, persisted formats, error messages callers rely on. This holds through every phase. Any intended behavior change requires explicit user approval before it is implemented.

## Specialization of design exploration: archaeology survey

Replace the large-feature design step "explore the relevant parts of the codebase first" with a survey of the component. Run Explore subagents in parallel — one per angle, launched in a single message: each angle gets an independent context, so coverage is diverse and the raw file dumps stay out of the main context; only the synthesized reports come back. The angles:

1. **Structure**: every module/class/function in the component; the call graph; public surface vs internals; which layers merely delegate.
2. **Dead-weight inventory**, through the four /simplify lenses:
   - *Reuse*: code re-implementing something the codebase already has; name the existing helper.
   - *Simplification*: redundant or derivable state, copy-paste with slight variation, deep nesting, dead code.
   - *Efficiency*: wasted work — redundant computation, repeated I/O, sequential independent operations.
   - *Altitude*: special cases stacked on shared infrastructure where the underlying mechanism should be generalized. This is the primary lens — accreted layers are usually altitude failures.
3. **Test census**: for each test, what behavior it pins. Mark tests of removed behavior, tests that only exercise mocks or trivialities, duplicate coverage, and **over-mocked tests** — tests whose setup mocks or monkeypatches the component's own internals, or any collaborator that is not a true process boundary (network, clock, subprocesses, externally-owned storage; a tmp dir is real I/O, not a boundary). Such tests pin wiring, not behavior: they can pass despite broken behavior and break on harmless restructuring, so they are unreliable in both directions. For each over-mocked test, record what behavior (if any) it pins beneath the mocks. If a module has no test coverage at all, flag it in the plan: no deletion or layer-collapse happens in that module until either the user explicitly accepts the untested-refactor risk or a minimal characterization test is added first.
4. **Instruction-text census** (only when the component carries LLM-facing text: system prompts, tool and skill descriptions, agent instructions, schema `description` fields, few-shot examples): find contradictions between instructions, near-duplicate guidance that drifted apart, references to tools or behavior that no longer exist, and the same concept named differently across surfaces. Unlike comments, this text is load-bearing — it steers model behavior — so the survey flags; it does not fix.

**Targeted history check** (after the survey, not a survey angle of its own): do not dig through git history wholesale. Consult `git log`/`git blame` for two classes of item: (a) anything the survey flags as "unclear why this exists", and (b) every migration-shaped deletion candidate — v1/v2 pairs, compatibility shims, never-set config flags, paths with no callers — regardless of how dead it looks, because an in-flight migration's guard looks exactly like dead weight. Recent introduction or recent commits touching the item are evidence of an in-flight migration; treat such items as guards until proven otherwise. Items still unclear after the history check go to the Chesterton's fences list.

## Specialization of the plan

In addition to the standard plan structure, the plan MUST contain:

- **Current-state map**: the layers and what each actually adds (often: nothing).
- **Target design**: how the component would be written today, coherently, from scratch. The plan converges the code to it; it does not patch layers with more layers.
- **Scope gate**: if the survey reveals the component is really several tangled components, or the target design cannot be reached in one reviewable branch, propose a staged sequence of /unify-sized chunks and let the user pick the first. Never expand scope beyond the named component without explicit approval.
- **Diff shape**: a good /unify PR usually deletes more than it adds across the target component. If the plan expects net growth, explain why the growth is the consolidated target design replacing larger hidden complexity, not another layer.
- **Deletion ledger**: every abstraction, test, comment, flag, or compatibility path to be dropped, each with evidence it is safe. Evidence means whichever of these apply: a callers search from the repository root (covering tests, generated code, and string-name references — DI registries, serialized configs, migrations), a config-value search across all environments, a test run, git history. For migration-shaped candidates the Targeted history check is mandatory in addition to the usage evidence, not an alternative to it. A "fully ramped" or "no traffic" claim must cite the rollout/config source or a telemetry/log query — a static callers search does not establish absence of traffic. Categories:
  - abstractions: interfaces with one implementation, indirection with a single client, config flags never set in any environment, v1 paths superseded by v2 — for superseded paths the evidence must show the migration is complete (v2 fully ramped, v1 with no remaining callers or traffic), not merely that v2 exists; if the superseded path is part of the externally reachable surface, its deletion is a behavior change and additionally requires approval under Behavior changes, even with empty caller and traffic evidence;
  - tests: tests of deleted behavior, duplicate coverage (cite the surviving test that keeps the coverage), and every over-mocked test from the census with an explicit disposition — *delete* if it pins nothing beyond the wiring, *rewrite* against real code if the behavior beneath the mocks is worth keeping. Deleting a module's only test is allowed, but the module then falls under the census no-coverage rule (minimal characterization test first, or explicit user acceptance of the risk);
  - comments: descriptions of behavior that no longer exists, finished-migration TODOs, changelog-style narration;
  - instruction text (when present): references to tools or behavior proven removed are stale-reference cleanup, deletable with the same evidence standard as code. Duplicated guidance to merge into one wording (cite each absorbed copy) and contradictions (name the resolution and the losing instruction) are semantic edits — they go through the Behavior changes section. A contradiction that cannot be confidently resolved goes to Chesterton's fences with the competing instructions quoted.
- **Microbug ledger**: obvious small correctness bugs discovered inside the target component while surveying or collapsing layers. UI-heavy components often have many: stale state, duplicate event handling, async races, missing cleanup, broken empty/loading/error states, focus or keyboard regressions, inconsistent validation, dead controls. Non-UI components get the same treatment for local bugs with obvious intended behavior. Classify each as *must fix now* (local bug, intended behavior is obvious, fix is small, and regression/characterization coverage is feasible), *needs approval* (observable behavior or product semantics change), or *follow-up* (real bug but outside this unify scope).
- **Chesterton's fences**: things that look dead but could not be proven dead. List them explicitly for the user; never silently delete them.
- **Behavior changes**: per the hard default above, any externally observable change (including dropping a deprecated-but-reachable path, and any semantic edit to LLM-facing instruction text) goes in its own section for explicit user approval; absent approval, it stays out of scope.

## Specialization of implementation

- Order subtasks so the tree stays green after each one: typically prove-dead-and-delete first, then collapse layers, then reshape to the target design. Each subtask leaves tests passing.
- A test is deleted only in the same subtask that removes the behavior it pins, or with deletion-ledger evidence that it pins nothing.
- An over-mocked test marked *rewrite* is replaced in the same subtask that touches the behavior it pins: write the real test first, see it pass against the current code, then drop the mocked one. If the real test needs setup infrastructure that does not yet exist, add that infrastructure as its own preceding subtask. Never re-point mock setups at the new structure.
- An approved instruction-text edit is verified with the repo's prompt evals or snapshot tests where they exist; absent those, quote before/after in the subtask summary so the review gates can judge the semantic delta.
- Chesterton's fence items may be deleted only after explicit per-item user confirmation, even if implementation-time exploration appears to prove them dead.
- If a behavior change surfaces during the implementation or review gates that was not in the approved plan, pause and surface it to the user; do not silently revert or silently keep it.
- A deletion-only subtask is reviewed as a diff (with its ledger evidence), not by running the deleted tests; per-component REVIEW with tests applies from the collapse phase onward.
- Microbugs marked *must fix now* are fixed in the same subtask that touches the affected code, with regression coverage. Do not silently bundle broader behavior or product changes into the refactor.
- Do not rewrite-from-scratch in one subtask unless the component is small enough that the whole replacement is one reviewable diff.
- Deletions leave no trace: never add "use X, not Y", "Y was removed", or deprecation-note comments. The target design is enforced structurally (delete the old path, stop exporting it), not by prose. A candidate that cannot be deleted stays untouched — never annotated.

## Specialization of REVIEW

Add to every REVIEW round four questions: **did this change delete more than it added across the target component?**, **did this change add a new layer instead of removing one?**, **did this change add or carry forward mocks/monkeypatching of the component's own internals?**, and **did this change add comments that narrate the refactor or steer callers ("use X, not Y") instead of enforcing the design structurally?** A unify diff that introduces a fresh wrapper, adapter, or compatibility flag — new test doubles for anything other than a true process boundary — or refactor-narrating comments — is a finding of the highest severity. Net negative line count is expected across the component as a whole; a file may grow when it absorbs the consolidated target design replacing several deleted ones — annotate such cases in the summary.

Deletion and behavior-preservation review is adversarial. For every deleted abstraction, path, test, flag, comment, or instruction, REVIEW must try to disprove the deletion ledger: find missed callers, serialized references, config values, rollout evidence, traffic evidence, tests that still pin behavior, or git history suggesting an in-flight migration. If the evidence is incomplete, the item becomes a Chesterton's fence, not a deletion.
