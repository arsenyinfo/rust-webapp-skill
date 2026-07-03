# Design taste (shared reference)

Used by build's overengineering review lens, refactor's dead-weight survey, and sweep's simplification lens. Language-agnostic — apply the spirit in whatever language the code is written in. It never overrides a mode's supervision policy or safety contract.

## The four /simplify lenses

- **Reuse**: code re-implementing something the codebase already has — name the existing helper.
- **Simplification**: redundant or derivable state, copy-paste with slight variation, deep nesting, dead code.
- **Efficiency**: wasted work — redundant computation, repeated I/O, sequential independent operations that could run together.
- **Altitude**: special cases stacked on shared infrastructure where the underlying mechanism should be generalized. Accreted layers are usually altitude failures — collapse the special-case-on-shared-infra tower, don't build it taller.

## The posture every simplification moves toward

- **Boring and explicit beats clever.** The straightforward version is the target. Cleverness, indirection, and framework-flavored machinery must earn their place; by default they are the defect, not the fix.
- **Type-heavy.** Model closed sets of states as enums/unions and domain identifiers as dedicated types (newtypes/branded types), not raw strings, bools, tuples, or long positional argument lists. Make invalid states unrepresentable. Stringly-typed and boolean-flag APIs are findings.
- **Early error handling at boundaries.** Validate untrusted input at the public entry point and convert it into domain types immediately — do not thread raw input and validation deep into the call graph. Prefer domain error types over generic strings; preserve error context. Swallowed errors, silent fallbacks, and panics/`unwrap`-style crashes on library paths are findings.
- **Abstractions pay rent immediately.** An interface/trait with a single implementation, a `FooManager`/`FooService`/`FooFactory` introduced only to ease testing, premature generics, or indirection added to avoid understanding the data flow — all findings.
- **Pragmatic footprint.** Minimal public surface, minimal justified dependencies, zero dead code. A fix must not expand the API surface or pull in a dependency for something trivial.
