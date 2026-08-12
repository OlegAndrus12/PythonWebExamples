# statusboard — dockerized with uv

The uptime board from [`module01/04_uv/`](../../module01/04_uv/), unchanged, in five
Dockerfile instructions. The application code, templates, `pyproject.toml` and `uv.lock`
are a byte-for-byte copy — only [Dockerfile](Dockerfile), [.dockerignore](.dockerignore)
and [docker-compose.yaml](docker-compose.yaml) are new.

Its twin [`../statusboard-poetry/`](../statusboard-poetry/) is the identical application
packaged with Poetry, on port 8001. Run both and compare the images.

Module 01 asked *how do I get a reproducible environment on my laptop?* and answered
`uv.lock`. This directory asks the same question about a server and gives the same
answer — the lock file is what `uv sync --frozen` reads inside the build.

The walkthrough is **Part 6** of [../README.md](../README.md). This is the short version.

## Run it

```bash
cd module03/statusboard

docker compose up --build
```

Open <http://localhost:8000>. The board probes six public sites and shows status and
latency; the second tab reads Cloudflare's public incident API. Both need outbound
internet from the container.

Without Compose:

```bash
docker build -t statusboard .
docker run --rm -p 8000:8000 statusboard
```

## The whole Dockerfile

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app
COPY . .
RUN uv sync --frozen --no-dev
CMD ["/app/.venv/bin/flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "8000"]
```

- The base image is Python 3.12 with the `uv` binary already in it, so there is nothing
  to install before installing dependencies.
- `--frozen` installs exactly what `uv.lock` pins, or fails. No silent re-resolution —
  that is the whole reason the lock file is committed.
- `--no-dev` skips the `[dependency-groups] dev` entries. Twelve packages instead of
  forty-odd.
- `--host 0.0.0.0` is mandatory. Flask's default `127.0.0.1` binds only the container's
  own loopback, so `-p 8000:8000` would forward to a socket nothing is listening on.
- No `EXPOSE`: it is documentation only and changes nothing about what is reachable.

## What minimal costs

Deliberate trade-offs, each a reasonable exercise:

| Left out | Consequence |
| --- | --- |
| Dependency layer copied before source | Editing `app.py` re-runs `uv sync` |
| Second stage | `uv` ships to production (268 MB) |
| `USER` | Runs as root |
| `HEALTHCHECK` | `docker ps` shows `Up`, never `healthy` |
| gunicorn | Flask's dev server, which prints a warning saying not to use it |

## Against the Poetry build

| | here (uv) | [../statusboard-poetry/](../statusboard-poetry/) |
| --- | --- | --- |
| Dockerfile instructions | 5 | 6 |
| Tool comes from | official base image | a `pip install` layer |
| Install | `uv sync --frozen --no-dev` | `poetry install --without dev` |
| Reproducibility | explicit `--frozen` | implicit; stale lock is an error |
| Venv location | `/app/.venv` by default | needs `POETRY_VIRTUALENVS_IN_PROJECT` |
| Final image | 268 MB | 332 MB |

Both install the same twelve packages at the same versions. The 64 MB difference is
entirely what the tool leaves behind in the finished image.

## State

The watch list is `services.json` on disk, so anything added through the UI is lost when
the container is removed. The compose file bind-mounts that one file back to the host as
a stopgap. `services.py`'s own docstring explains why the real answer is a database —
which is where `module05/` picks up.

## Inherited clutter

`bandit_demo/`, `mypy_demo/`, `conflict/`, `pyproject.reference.toml` and
`.pre-commit-config.yaml` came along with the copy and belong to the module01 packaging
lecture, not to Docker. They are all listed in `.dockerignore`, so `COPY . .` never sees
them. Check what actually shipped:

```bash
docker run --rm statusboard ls /app
```
