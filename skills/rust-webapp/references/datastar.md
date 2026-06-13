# DataStar

Use DataStar in this skill only when `HTMX + Alpine.js` stops being the simplest fit.

Default recommendation:

- `HTMX + Alpine.js` for simpler CRUD, forms, filters, toggles, tabs, and inline edits.
- `DataStar` for more advanced reactive Rust pages, especially when SSE is central.

## Setup

This skill's standard `templates/base.html` keeps the DataStar script commented out by default so the starter does not preload both frontend stacks.

If you choose DataStar for a page or app, treat it as a replacement for `HTMX + Alpine.js` on that interaction surface.
In this skill's standard `templates/base.html`, comment out or remove the HTMX and Alpine `<script>` tags, then uncomment the DataStar script or include DataStar in your `<head>` before relying on any `data-*` attributes:

```html
<script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.2/bundles/datastar.js"></script>
```

## When To Choose It

Choose DataStar when the Axum app needs one or more of these:

- realtime or live-updating UI
- long-lived `text/event-stream` responses
- one backend response patching multiple regions over time
- one feature needing both local reactive state and server-pushed updates

Good fits in this skill:

- import/progress pages
- live dashboards
- collaborative or activity-style views
- search or filter pages that are becoming awkward with HTMX swaps plus Alpine state

If the page is ordinary CRUD, stay with `HTMX + Alpine.js`.

## Mental Model

DataStar combines:

- frontend reactivity via `data-*` attributes and signals
- backend-driven updates via HTML or SSE responses

For this Rust skill, keep the same overall architecture:

- Askama renders HTML
- Axum handlers remain the source of truth
- client-side signals are for transient UI state, not business truth

The upstream docs are explicit here: most state should stay in the backend, and signals should be used sparingly.

## Template Patterns

The main DataStar attributes worth using in this skill are:

- `data-signals`
- `data-bind`
- `data-text`
- `data-show`
- `data-attr`
- `data-class`
- `data-computed`
- `data-effect`
- `data-on:*`
- `data-indicator`

Minimal example:

```html
<section data-signals="{ query: '', loading: false }">
    <input
        type="search"
        data-bind:query
        data-on:input__debounce.250ms="@get('/search')"
        data-indicator:loading
    >

    <p data-show="$loading" style="display: none">Loading...</p>
    <div id="results"></div>
</section>
```

Notes relevant to Askama templates:

- keep stable IDs on top-level patch targets
- keep expressions short
- use `data-computed` for derived values, not side effects
- use `data-effect` only when signal changes must trigger an action
- attribute order matters, for example `data-indicator` before `data-init`

## Backend Response Patterns

DataStar backend actions can consume:

- `text/html`
- `text/event-stream`
- `application/json`

For this skill, the important paths are:

### `text/html`

Use for simple one-shot updates.

Return a fragment with a stable wrapper ID and let DataStar morph it into the existing DOM.

### `text/event-stream`

Use when the Rust handler needs to emit multiple updates over time.

This is the main reason to choose DataStar in this skill.

The two key SSE events are:

- `datastar-patch-elements`
- `datastar-patch-signals`

This lets one Axum handler do things like:

- patch a status region
- patch a progress region
- patch a signal used by the template
- later patch a final success state

all in one response stream.

### `application/json`

Can patch signals directly, but for this skill HTML patches or SSE are usually the primary fit.

## Rust-Specific Guidance

When using DataStar in this skill:

- keep Askama as the HTML source
- keep Axum handlers authoritative
- prefer the SDK or a well-formed SSE response helper instead of hand-rolling event text when possible
- keep partial templates small and wrapper IDs stable
- do not move business logic into frontend expressions

If the feature does not need streaming or richer reactive coordination, prefer `HTMX + Alpine.js` instead.

## Pitfalls

- forgetting stable IDs on morphed elements
- overusing signals instead of fetching fresh backend state
- putting too much logic in expressions
- mixing HTMX and DataStar on the same widget
- choosing DataStar for a page that is just normal CRUD

## Constraints Worth Knowing

The official docs call out a few things that matter when deciding whether to use DataStar:

- expressions are evaluated dynamically, so CSP needs `unsafe-eval`
- signals are user-visible and user-modifiable, so backend validation is mandatory
- the framework strongly prefers backend-driven state and SSE-friendly flows

Those are real tradeoffs, not just implementation details.

## Read More

Read these before building a non-trivial DataStar page:

1. `https://data-star.dev/guide/getting_started`
2. `https://data-star.dev/guide/reactive_signals`
3. `https://data-star.dev/guide/backend_requests`
4. `https://data-star.dev/reference/attributes`
5. `https://data-star.dev/reference/actions`
6. `https://data-star.dev/reference/sse_events`
7. `https://data-star.dev/guide/the_tao_of_datastar`
8. `https://data-star.dev/reference/security`
