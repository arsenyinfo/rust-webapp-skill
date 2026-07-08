# Audit playbook

The SKILL.md gives you the dimension list, the severity buckets, and the report shape. This file is the operator's detail: for each dimension, the concrete red flag and what to grep or read to catch it, plus the multi-reviewer machinery that produces the verdict. Audit adversarially — hunt for the action that shouldn't be possible, not reasons it's probably fine. Every finding carries `file:line` evidence; a claim you can't point at is a hunch, not a finding.

## Dimensions — red flag and where to look

**Harness boundary.** Red flag: the model touches the world directly — raw shell, an HTTP client, or a DB handle handed to the model instead of a tool. Grep for `subprocess`, `os.system`, `exec(`, `eval(`, `requests.`, `fetch(`, raw SQL string-building inside the agent-call path. If the model can name an arbitrary command, there is no boundary.

**Model/harness responsibility split.** Red flag: code that should decide is asking the model to, or the model is doing deterministic work. Look for prompt text like "make sure to validate", "only if authorized", "sort these", "don't forget to check permissions" — every one is a job the harness abandoned. Also the inverse: a tool whose body just forwards the model's free-text to another system with no parse/validate step.

**Tool naming (collapsing synonyms).** Red flag: two tools the model must disambiguate by vibes. Grep the registry for `get_`, `fetch_`, `load_`, `download_`, `read_`, `retrieve_` mixes over the same noun — pick one verb per meaning. Grep for generic verbs `execute`, `run`, `manage`, `process`, `handle`, `do_`, `call_api` — these collapse many actions into one name and force the model to encode intent in a string arg. One verb, one meaning; if synonyms exist, the harness aliases internally and the model sees one surface.

**Tool schema quality.** Red flag: untyped or open params. Grep schemas for `"type": "string"` where an enum belongs, `"type": "object"` with no `properties`, missing `additionalProperties: false`, `**kwargs`, `Any`, `dict` params, or a single `payload`/`args` catch-all. Unbounded output: a `list_*`/`search_*` with no `limit`/pagination that can dump the whole table into context. No poka-yoke = the schema can't stop a bad call.

**Tool result & error quality.** Red flag: `return "Error: failed"`, bare exception strings, `str(e)`, HTTP status echoed with no interpretation, silent `None`/empty on failure. Grep for `except.*: return`, `raise`, `"error"`. Every result is the next observation: it must state success/partial/blocked/failed, the evidence, whether retry helps, and a `next_actions` hint. A result the model can't act on is a dead end in the loop.

**Determinism gaps.** Red flag: prompt text doing a validator's, sorter's, or state-machine's job. Read the system prompt for enumerated rules, format specs, ordering instructions, "always/never" clauses that a schema, FSM, or script should own. A rule repeated to patch a past failure is the tell — the fix belongs in code, not a fourth sentence of prompt.

**Risk classification & permission gates.** Red flag: broad or side-effecting tools with no gate. Grep for `send_message`, `send_email`, `write_`, `delete_`, `deploy`, `execute`, `transfer`, `charge`, `update_`, `post_` and confirm each has a risk class and a permission check *in code before execution*, not a prompt asking nicely. If the permission engine runs inside the model's reasoning, there is no gate.

**Side-effect safety.** Red flag: a committing action with no draft/preview twin. Look for `send_*` without a `draft_*`, `apply_*`/`deploy_*` without `preview_*`/`prepare_*`, DB writes with no dry-run. Anything external, destructive, or financial that fires in one step is unreviewable. Check retries too: non-idempotent commit auto-retried = double side effect.

**State model.** Red flag: implicit state carried in prose or scattered booleans; no explicit rejected transitions. For multi-step flows, look for an FSM (states + allowed edges) — if approval, plan, or "already sent" lives only in conversation history, compaction can erase it and a rejected step can re-fire. Grep for flags like `approved`, `is_sent`, `state =` and check whether an illegal transition is *rejected* or merely un-taken.

**Observability.** Red flag: you can't reconstruct a run from traces. Check that each tool call logs name, args (or hash), result, permission decision, and a trace/run ID as structured events — not free-text `logger.info(f"...")`. Secrets in logs: grep for logging of `token`, `key`, `password`, `authorization`, full request bodies, PII. If a failed run can't be replayed from the record, it can't be debugged.

**Eval coverage.** Red flag: no evals, or evals not tied to real failures. Look for a suite with state-verified cases (assert the world changed, not that a string appeared), adversarial cases (injection, tool misuse), and a regression case per past incident. Average accuracy with no pass^k / reliability measure means autonomy is being granted on vibes.

**Context hygiene.** Red flag: retrieved content (webpages, emails, tickets, tool output, RAG chunks) concatenated into the prompt as if trusted — an injection surface. Check there's a data/instruction boundary and that untrusted text can't override policy. Cache hazard: grep the prompt assembly for timestamps, request IDs, or volatile state at the *head* of a cacheable prompt.

## Severity recap

- **Critical** — an unauthorized destructive/financial/external side effect can fire without approval; secrets leak to logs or model context; tool ambiguity routes the model to the wrong external action; prompt-injected content can drive a gated tool.
- **Major** — broad tool (`execute`, `write_database`, `send_message`) unwrapped; commit with no draft twin; state only in prose; `Error: failed` results; no state-verified or regression evals; volatile data poisoning the cache prefix.
- **Minor** — verb-synonym drift not yet exploitable, thin tool descriptions, missing examples, naming polish, non-blocking ergonomics.

## Multi-reviewer pattern

One reviewer is one set of blind spots. Run several **independent** reviewers with distinct lenses and, deliberately, **diverse models/providers** — a reviewer sharing the builder's model and priors is an echo, not evidence. The point of a second opinion is a *different* opinion.

Lenses (one reviewer each, roughly):
- **Tool-design** — naming collisions, schema types, bounded output, result/error envelopes.
- **Permission/safety** — risk classes, gates, draft/commit split, injection surface, secret handling.
- **Eval/observability** — trace completeness, replayability, eval-to-failure coverage.
- **Architecture** — boundary, model/harness split, state model, determinism gaps.
- **Implementation** — does the code do what the design claims; dead gates, bypassed checks, TODO'd guards.

Each reviewer is an **agentic loop**, not a single prompt: it may read files, grep, glob, and inspect `git log`/`git blame` to map the repo and gather evidence before writing findings. It emits the structured verdict below.

The **aggregator** then: dedups issues on a stable key (file:line + mechanism, not wording); ranks by severity; surfaces themes several reviewers hit independently (a cross-reviewer agreement is a stronger signal); produces one prioritized fix plan; and **preserves meaningful dissent** — when a diverse-model reviewer flags what others missed, surface it as an open disagreement, don't average it into the noise floor. The minority report is often where the real bug is.

## Review output schema (per reviewer; aggregator emits the same shape over the merged set)

```json
{
  "reviewer": "permission-safety",
  "model": "provider/model-id",
  "verdict": "pass | pass_with_concerns | fail",
  "summary": "one paragraph: worst thing found and overall posture",
  "critical": [{"dimension": "side-effect-safety", "evidence": "tools/mail.py:42", "why": "send_email fires with no draft twin and no gate", "fix": "split draft_email/send_email; gate send"}],
  "major":    [{"dimension": "...", "evidence": "file:line", "why": "...", "fix": "..."}],
  "minor":    [{"dimension": "...", "evidence": "file:line", "note": "..."}],
  "recommended_fixes": ["ordered, highest-leverage first"],
  "missing_evals":     ["no state-verified case for the transfer flow"],
  "determinism_gaps":  ["prompt asks model to validate amount; move to schema"],
  "permission_gaps":   ["write_database exposed unwrapped, no risk class"]
}
```

Any single `fail`, or any unresolved critical, fails the aggregate verdict — the gate is the most skeptical reviewer, not the average.
