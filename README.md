# FamilyHub

FamilyHub is a local family expense tracker. It is the first piece of a DevOps learning lab: a working application you can run on your machine. Kubernetes, cloud infrastructure, CI/CD, and monitoring are not part of this version.

## Architecture

```text
Browser
   |
   v
React + TypeScript + Vite
   |
   | HTTP /api  (proxied by the Vite dev server)
   v
FastAPI + SQLAlchemy + Pydantic
   |
   | SQL
   v
PostgreSQL
```

| Piece | Role |
| --- | --- |
| `fet-ui` | Pages for login, expenses, categories, budget, and the dashboard |
| `fet-backend` | REST API, JWT authentication, Alembic migrations, demo seed |
| `db` | PostgreSQL 16, data stored in the named volume `postgres_data` |

Passwords are hashed with bcrypt. The API issues a signed JWT. The browser stores that token in `localStorage` and sends it as `Authorization: Bearer …`. Logout removes the token. Tables are created only by Alembic, not when the API process starts.

## Prerequisites

- Docker with Docker Compose v2
- Free local ports `5173` and `8000`. PostgreSQL is published on host port `5433` so it does not collide with a Postgres already using `5432`. Change `POSTGRES_PORT` in `.env` if `5433` is taken.

## Start the application

From the repository root:

```bash
docker compose up --build
```

The first build downloads images and installs dependencies, so it can take a few minutes. When the backend is healthy it:

1. Waits until PostgreSQL accepts connections
2. Runs `alembic upgrade head`
3. Seeds the demo user if that user does not exist yet
4. Starts the API

Open the app at [http://localhost:5173](http://localhost:5173).

Stop it with `Ctrl+C`, then `docker compose down`. Add `-v` only when you want to delete the database volume.

### Demo account

| Email | Password |
| --- | --- |
| `demo@example.com` | `Demo123!` |

The demo user has the default categories, sample expenses for this month and last month, and a monthly budget of **250 PLN (zł)**. Current-month spending is over that budget, so the dashboard shows a warning.

## URLs

| URL | What it is |
| --- | --- |
| http://localhost:5173 | FamilyHub UI |
| http://localhost:5173/login | Login |
| http://localhost:5173/register | Registration |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/health | API health check |

In Swagger, call `POST /api/auth/login`, copy `access_token`, click **Authorize**, and paste the token.

## Configuration

Environment variables have local defaults in `docker-compose.yml`. To override them:

```bash
cp .env.example .env
```

`.env` is gitignored. Do not commit real secrets. `JWT_SECRET` in the example is a development value only.

If you change `POSTGRES_PASSWORD`, set `DATABASE_URL` and `TEST_DATABASE_URL` to the same password. The hostname inside Compose is `db`, not `localhost`.

## Migrations

Migrations live in `fet-backend/alembic/versions` and run automatically on backend startup.

Run them again by hand:

```bash
docker compose exec backend alembic upgrade head
```

Create a new revision after changing `fet-backend/app/models.py`:

```bash
docker compose exec backend alembic revision -m "describe the change"
```

Edit the generated file so it matches the model change, then upgrade.

## Seed data

```bash
docker compose exec backend python -m app.seed
```

The seed is idempotent. If `demo@example.com` already exists, it does nothing. To load a fresh demo database:

```bash
docker compose down -v
docker compose up --build
```

New registrations receive these categories: Food, Rent, Transport, Shopping, Entertainment, Travel, Utilities, Other. The default currency is PLN (zł).

## Tests

Backend tests use a separate PostgreSQL database, `familyhub_test`. They apply the Alembic migrations, then roll the data back by truncating tables. They do not use SQLite.

```bash
docker compose exec backend pytest
```

## API

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register` | Create an account and default categories |
| POST | `/api/auth/login` | Return a JWT |
| GET | `/api/auth/me` | Current user |
| GET, POST | `/api/expenses` | List (filter and sort) or create |
| GET, PUT, DELETE | `/api/expenses/{id}` | Read, update, or delete one expense |
| GET, POST | `/api/categories` | List or create |
| PUT, DELETE | `/api/categories/{id}` | Rename or delete |
| GET, PUT | `/api/budget` | Read or set the monthly budget |
| GET | `/api/dashboard` | Month totals, category breakdown, recent expenses |

Expense list filters: `category_id`, `date_from`, `date_to`, `q`. Sort fields: `date`, `amount`, `description`, `category`, `created_at`. Order: `asc` or `desc`.

Users only see their own rows. A category that still has expenses cannot be deleted.

## Troubleshooting

**Ports already in use.** Stop the other process or set `FRONTEND_PORT`, `BACKEND_PORT`, or `POSTGRES_PORT` in `.env`. The database is published on `5433` by default because many machines already run Postgres on `5432`. Inside Compose the database is still `db:5432`.

**Backend keeps restarting or never becomes healthy.** Check `docker compose logs backend`. The usual cause is PostgreSQL not ready yet, or `DATABASE_URL` not matching the database user and password.

**UI loads but API calls fail.** Confirm `http://localhost:8000/health` returns `{"status":"ok"}`. The Vite server proxies `/api` to the backend service.

**Demo data looks stale or the seed says it skipped.** The named volume keeps data across restarts. Remove it with `docker compose down -v` and start again.

**Tests cannot connect.** Run them with `docker compose exec backend pytest` so they use the Compose network and `TEST_DATABASE_URL`.
