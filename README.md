# Skills

Just another collection of skills for coding agents.

- `large-feature`: rigorous workflow for larger features and refactors.
- `unify`: refactor accreted components into one coherent design.
- `dialectic`: prove and counter-prove claims with parallel agents before concluding. 
- `investigate`: evidence-first debugging and root cause investigation. 
- `rust-webapp`: build full-stack Rust web apps with Axum, SQLx, HTMX, Alpine.js, and Neon. No React, no TypeScript, no Webpack, no Vite, no Babel, no yarn, no pnpm.
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
