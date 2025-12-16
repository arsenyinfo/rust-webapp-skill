# rust-webapp-skill

Claude Code skill for building full-stack web applications with Rust.

## Why This Stack?

- **Rust + Axum**: Type-safe, fast, reliable backend - no runtime surprises
- **HTMX + Alpine.js**: Modern interactivity without the JavaScript framework complexity
- **Askama templates**: Compile-time checked HTML - template errors caught before runtime
- **PicoCSS**: Clean styling out of the box, no CSS framework bloat
- **Neon**: Serverless PostgreSQL - instant dev branches, auto-scaling, no server management
- **Single Docker container**: Simple deployment, easy to host anywhere

The result: a pragmatic, maintainable stack that's productive without drowning in JavaScript tooling.

## Install

```bash
curl -sSL https://raw.githubusercontent.com/arsenyinfo/rust-webapp-skill/main/install.py | python3
```

Installs to `~/.claude/skills/rust-webapp/`.

## Prerequisites

```bash
npm i -g neonctl
brew install jq
cargo install sqlx-cli --features postgres,native-tls
```

Set up [Neon](https://neon.com):
1. Create a free account at [neon.com](https://neon.com)
2. Create a project and get your API key
3. Set environment variables:
```bash
export NEON_API_KEY=your-key
export NEON_PROJECT_ID=your-project-id
```

The skill creates ephemeral database branches for each app - isolated environments that auto-expire, keeping your project clean.

## Usage

In Claude Code, the skill activates when you ask to build a web app:

- "Build a todo list app"
- "Create a voting application"
- "Make a simple blog"

### Flow

1. **Scaffold** - creates project structure with Neon branch
2. **Model** - define data models and migrations
3. **Backend** - implement route handlers
4. **Frontend** - update Askama templates with HTMX/Alpine
5. **Validate** - run checks (cargo check, clippy, tests, release build)
6. Repeat 2-5 until validation passes

## References

Based on the approach from [app.build: Production Framework for AI-Generated Applications](https://arxiv.org/abs/2509.03310).

## License

MIT
