# Project One Documentation

Short, practical documentation for this repository.

## Contents

- [Architecture](./docs/architecture.md): components, data flow, and runtime services.
- [Use Case Example](./docs/use-case-example.md): one end-to-end sensor ingestion scenario.
- [Use In Other Projects](./docs/use-in-other-projects.md): how to reuse `commonpackages` and integrate with your own app.

## Quick Start

Run the platform:

```bash
docker compose up --build
```

Then open:

- Gateway API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- RabbitMQ UI: `http://localhost:15672`
- pgAdmin: `http://localhost:5050`
