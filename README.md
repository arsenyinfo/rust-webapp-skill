# Skills

My reusable agent skills.

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

## Skills

- `rust-webapp`: build full-stack Rust web apps with Axum, SQLx, HTMX, Alpine.js, and Neon.
- `large-feature`: rigorous workflow for larger features and refactors.
- `unify`: refactor accreted components into one coherent design.

## Layout

Each skill lives at `skills/<name>/SKILL.md`. No manifest is required for `npx skills add`; it discovers this layout automatically.
