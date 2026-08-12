# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Lecture materials for a course called "Web Development with Python". It is **not one application** — it is a collection of independent, self-contained example projects, one per lecture topic. There is no root `pyproject.toml`, no shared virtualenv, no CI, no linter config, and no test suite (the `tests/` directories contain only an empty `__init__.py` left by `poetry new`).

Consequences for working here:

- Always `cd` into the specific project directory before running anything. Commands are never run from the repo root.
- Examples are written to *teach a concept*, so they are deliberately minimal, sometimes incomplete, and progressively re-implement the same ideas (SQLAlchemy models, auth, config) with increasing sophistication across modules. Do not "unify" or refactor across projects, and do not fix unrelated rough edges in an example unless asked — the simplified form is usually the point.
- `.env` files, `config.ini`, and compose credentials are committed on purpose (`admin`/`admin`, sample SMTP + JWT secrets). `.gitignore` only excludes `node_modules/`. These are throwaway teaching values, not leaked production secrets.

## Layout

Numbered `moduleNN/` directories follow the lecture order; the two named directories are the larger capstone apps.

| Path | Topic |
| --- | --- |
| `module01/` | SOLID principles (`solid/S,O,L,I,D/`) and design patterns (proxy, observer, template method, Django-style middleware). Standalone snippets, no packaging. |
| `module02/` | `readme.md` only — reference tables for virtualenv/pipenv/pyenv/pipx/poetry and version constraint syntax. |
| `module03/` | Docker & docker-compose. Polyglot on purpose: Python, Node, Go, Java, Ruby containers. `microservices/`, `flask-node/` (Flask + Express + Mongo), `postgres_ex/` (Postgres + pgAdmin). |
| `module04/` | HTTP and web servers: `simple-http/` and `httpv2/` (stdlib `http.server`), `flask_new/` (Flask + NewsAPI), `async_ex/` (asyncio, aiohttp, websockets, CPU- vs IO-bound). |
| `module05/` | Raw `sqlite3` (`src/module05/sql/`) then SQLAlchemy ORM (`sql_alchemy_ex.py`). |
| `pydantic_ex/` | Numbered `01.py`–`13.py` walkthrough of Pydantic v2, plus `field.py`, `forbid_extra.py`, `settings_ex.py`. |
| `todos/` | Flask + SQLAlchemy + Alembic + Postgres, server-rendered Jinja templates, session auth. |
| `zoo_api/` | The most complete example: FastAPI + SQLAlchemy + Alembic + Postgres + Redis + JWT + email verification, fully containerized. |

## Poetry projects

`pydantic_ex/`, `module04/async_ex/`, `module04/flask_new/`, `module05/`, `todos/`, `zoo_api/` each have their own `pyproject.toml` + `poetry.lock`. All use the src-layout convention `packages = [{include = "<name>", from = "src"}]` and require Python >=3.13 (`async_ex` is >=3.12).

```bash
cd <project> && poetry install
poetry run python src/pydantic_ex/07.py    # scripts are run individually
```

Files under `module01/`, `module03/`, `module04/simple-http/`, and `module04/httpv2/` are not packaged — run them with plain `python`, from inside their own directory (they open sibling files like `clock.html` by relative path).

There is no test runner configured. Adding tests means `poetry add --group dev pytest` in the specific project first.

## zoo_api

Runs only under docker-compose: `settings.py` sets `env_file=None`, so configuration comes from the process environment injected by `env_file: .env` in `docker-compose.yaml`, and `DB_DOMAIN=db` / the hardcoded `redis` host in `services/auth.py` are compose service names that don't resolve on the host.

```bash
cd zoo_api
docker compose up --build          # api :8000, postgres :5432, pgadmin :5050, redis :6379
```

`run.sh` is the container entrypoint: waits for Postgres with `pg_isready`, runs `alembic upgrade head`, then starts uvicorn with `--reload` (the source tree is bind-mounted, so edits reload live).

Migrations must run in the container, since the DB hostname is only resolvable there:

```bash
docker compose exec fastapi-server poetry run alembic revision --autogenerate -m "message"
docker compose exec fastapi-server poetry run alembic upgrade head
```

`alembic.ini` points `script_location` at `src/migrations`, and `src/migrations/env.py` overrides `sqlalchemy.url` from `settings.DB_URL` — the `driver://user:pass@localhost/dbname` placeholder in the ini is never used.

### Layering

`main.py` (app + middleware + router registration, all routers mounted under `/api`) → `src/routers/` (HTTP concerns, dependency wiring) → `src/repository/` (SQLAlchemy queries) → `src/database/models.py`. Cross-cutting pieces sit alongside: `src/schemas/` (Pydantic request/response models), `src/services/` (auth, email), `src/settings.py`, `src/roles.py`. Repository functions are declared `async` but perform synchronous SQLAlchemy calls — that's the shape used throughout; match it.

Auth (`src/services/auth.py`) is a singleton `auth_service = AuthService()`. Tokens are HS256 JWTs carrying a `scope` claim that distinguishes `access_token` from `verification_token`; `get_current_user` checks Redis (`email:<addr>`, pickled `User`, 10 min TTL) before falling back to the DB. Endpoints are protected two ways: `Depends(auth_service.get_current_user)` for plain authentication (see the router-level dependency in `routers/cats.py`), and the `RoleAccess([Role.admin, ...])` callable class in `src/roles.py` for role checks (`routers/owners.py`). Email verification is sent via `BackgroundTasks` through fastapi-mail against a Mailtrap sandbox, rendering `src/services/templates/email_verification.html`.

## todos

Docker-compose here provides **only** Postgres and pgAdmin — the Flask app is meant to run on the host (`config.ini` has `DOMAIN=localhost`), and `src/main.py` calls `app.run(host="0.0.0.0", port=3000, debug=True)` at import time, so running the module starts the server.

```bash
cd todos
docker compose up -d               # postgres :5432, pgadmin :5050
poetry run alembic upgrade head    # from todos/, works as-is
```

Be aware before touching it: the app's imports are inconsistent and it does not currently start. `src/main.py` and `src/database/repository.py` use flat imports (`from config import config`, `from utils import hash_password`), which need `src/` on `sys.path`, while `src/database/db.py` uses `from ..config import config`, which needs `todos/` as the root — and `src/database/` has no `__init__.py`. Importing `database.db` with `src/` as the working directory raises `ImportError: attempted relative import beyond top-level package`. Alembic works because `migrations/env.py` imports `src.database.db` from the `todos/` directory, where the relative import resolves. Fix the import scheme (pick one root) before trying to run the web app.

Config comes from `src/config.ini` via `configparser` (`[DB]` and `[APP]` sections) rather than pydantic-settings; passwords are plain SHA-256 in `src/utils.py`; sessions are Flask cookie sessions. Note `src/routers/` exists but every file in it is empty.

## Other runnable examples

```bash
cd module04/flask_new && poetry run python src/flask_new/app.py   # :3000, needs NEWS_API_KEY in src/flask_new/.env
cd module04/simple-http && python3 main.py                        # :8001
cd module03/flask-node && docker compose up --build               # Flask :5001, Express :3000, Mongo
cd module03/microservices && docker compose up --build            # multi-language microservice demo
```
