# Skills

Just another collection of skills for coding agents.

- `tokenmaxxer`: one serious-work skill with five modes selected by the first argument word — `build` (features, cross-cutting changes, root-caused fixes, with a fast path for trivial changes that keeps the review gate), `refactor` (refactor an accreted component into one coherent design), `sweep` (unattended overnight cleanup of a named area — fan out explorers, fix tiny bugs and dirty code, verify with an independent model, ship themed commits as subsystem draft PRs), `experiment` (metric-driven experimentation — a reviewed hypothesis tree you approve, an autonomous batch of runs gated on evidence rather than the raw metric, a report proposing the next batch), and `followup` (work through the out-of-scope findings every mode records to a per-repo ledger, with your decisions, review-first).
- `dialectic`: prove and counter-prove claims with parallel agents before concluding. 
- `investigate`: evidence-first debugging and root cause investigation. 
- `rust-webapp`: build full-stack Rust web apps with Axum, SQLx, HTMX + Alpine.js (or DataStar for SSE-heavy UIs), and Neon. No React, no TypeScript, no Webpack, no Vite, no Babel, no yarn, no pnpm.
- `ml-project`: opinionated workflow for ML projects.

Kudos for inspiration and ideas go to:
- [cc-thingz](https://github.com/umputun/cc-thingz) by [@umputun](https://github.com/umputun);
- [appdotbuild](https://github.com/neondatabase/appdotbuild-agent) by the [@neondatabase](https://github.com/neondatabase) team;
- [reharness](https://github.com/bes-dev/reharness) by [@bes-dev](https://github.com/bes-dev);

## Install

List available skills:

```bash
npx skills add arsenyinfo/skills --list
```

Install one skill globally for Claude Code:

```bash
npx skills add arsenyinfo/skills --skill rust-webapp -g -a claude-code
```

Install all skills:

```bash
npx skills add arsenyinfo/skills --skill '*' -g -a claude-code
```

## Layout

Each skill lives at `skills/<name>/SKILL.md`. No manifest is required for `npx skills add`; it discovers this layout automatically.
