# My App

Built with Rust (Axum) + HTMX + [Neon](https://neon.com) (serverless PostgreSQL).

## Development

Run the app locally:
```bash
source .env
cargo run
```

App runs at http://localhost:8000

## Database

Migrations run automatically on startup. To run manually:
```bash
source .env
sqlx migrate run
```

## Build

```bash
cargo build --release
```

## Docker

Build:
```bash
docker build -t myapp .
```

Run:
```bash
docker run -p 8080:80 -e DATABASE_URL="$DATABASE_URL" myapp
```

## Deploy

The Dockerfile produces a minimal image ready for deployment. Set `DATABASE_URL` environment variable in your hosting platform.
