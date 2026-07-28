# FastAPIBlog
 
A blogging platform built with FastAPI, combining a server-rendered frontend (Jinja2) with a JSON API, backed by async SQLAlchemy and JWT authentication.
 
## Features
 
- **User accounts** — registration, login, and profile pages with profile picture uploads
- **JWT authentication** — access tokens via `OAuth2PasswordBearer`, passwords hashed with Argon2 (`pwdlib`)
- **Password reset flow** — single-use, hashed, time-limited reset tokens sent via email
- **Posts** — create, view, and browse posts with pagination and author info eager-loaded for performance
- **Per-user post pages** — view all posts by a specific user
- **Dual response modes** — HTML pages for the browser (Jinja2 templates) and JSON responses for `/api/*` routes, including consistent error handling for both
- **Database migrations** — schema changes managed with Alembic
- **Async throughout** — built on `AsyncSession` / async SQLAlchemy for non-blocking database access
- **Tests** — automated test suite included
- **Deployment** - deployed as a containerized service on Google Cloud Run, 
database hosted on Neon (serverless Postgres)

## Tech Stack
 
- **Framework:** FastAPI
- **Database:** SQLAlchemy (async), Alembic for migrations
- **Auth:** JWT (`pyjwt`), Argon2 password hashing (`pwdlib`)
- **Templating:** Jinja2
- **Email:** SMTP-based email sending for password resets
- **Config:** `pydantic-settings`, loaded from `.env`

## Link

https://fastapi-service-396129845196.europe-west3.run.app
