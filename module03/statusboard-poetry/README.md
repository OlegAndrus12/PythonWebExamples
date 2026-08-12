# statusboard — dockerized with Poetry

The uptime board from [`module01/03_poetry/`](../../module01/03_poetry/), unchanged, in
six Dockerfile instructions. Its twin [`../statusboard-uv/`](../statusboard-uv/) is the
identical application packaged with uv — same `app.py`, same templates, same CSS, byte
for byte. Only the manifest, the lock file and the Dockerfile differ.

Run both at once and compare. That is the point of having two.

## Run it

```bash
cd module03/statusboard-poetry

docker compose up --build
```

Open <http://localhost:8001>. (The uv build takes 8000, so both fit.)

Without Compose:

```bash
docker build -t statusboard-poetry .
docker run --rm -p 8001:8000 statusboard-poetry
```

## The whole Dockerfile

```dockerfile
FROM python:3.12-slim-bookworm
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN pip install --no-cache-dir poetry==2.4.1
WORKDIR /app
COPY . .
RUN poetry install --without dev
CMD ["/app/.venv/bin/flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "8000"]
```

Six instructions against uv's five. The extra one is `pip install poetry`: uv publishes a
base image with the tool already in it, Poetry does not, so Poetry has to be installed
before it can install anything else.

- **`POETRY_VIRTUALENVS_IN_PROJECT=true`** puts the venv at a predictable `/app/.venv`
  instead of `~/.cache/pypoetry/virtualenvs/<project>-<hash>-py3.12`, which is awkward to
  name in a `CMD`. See the trap below.
- **`poetry==2.4.1`** is pinned to the version that generated `poetry.lock`. Unpinned,
  this line quietly changes what builds your image.
- **`--without dev`** skips `[tool.poetry.group.dev.dependencies]` — ruff, pytest, bandit,
  mypy, pre-commit, types-requests. Twelve packages instead of forty.
- **No `--frozen` flag exists** and none is needed: Poetry refuses to install from a
  `poetry.lock` that no longer matches `pyproject.toml`. `package-mode = false` in
  `pyproject.toml` is why `--no-root` is not needed either.

## The trap: `POETRY_VIRTUALENVS_CREATE=false`

The advice you will find most often is to disable Poetry's virtualenv entirely, on the
reasoning that a container is already isolated. It is one line shorter and it is a bad
idea, because **Poetry itself is installed in that same system Python.**

Measured on this project — build it both ways and read the output of `poetry install`:

| | `VIRTUALENVS_CREATE=false` | `VIRTUALENVS_IN_PROJECT=true` |
| --- | --- | --- |
| Poetry reports | `7 installs` | `12 installs` |
| Packages visible to the app | ~50 | 12 |
| Where `requests` came from | **Poetry's dependency tree** | `poetry.lock` |
| Image size | 309 MB | 332 MB |

Poetry depends on `requests`, `urllib3`, `certifi`, `idna` and `charset-normalizer`
itself, so with a shared environment those five were *already satisfied* and Poetry
skipped them. The application then imported whichever versions Poetry needed. Here they
happened to match the lock file; nothing guarantees that, and nothing tells you when it
stops being true. A lock file you do not actually install from is decoration.

The in-project venv costs 23 MB and removes the whole class of problem.

## Poetry vs uv, on this project

| | [../statusboard-uv/](../statusboard-uv/) | here |
| --- | --- | --- |
| Dockerfile instructions | 5 | 6 |
| Tool comes from | official base image | `pip install` layer |
| Install command | `uv sync --frozen --no-dev` | `poetry install --without dev` |
| Reproducibility flag | explicit `--frozen` | implicit; stale lock is an error |
| Excluding dev deps | `--no-dev` | `--without dev` |
| Image size | 268 MB | 332 MB |

The 64 MB gap is Poetry and its ~40 dependencies sitting in the runtime image with
nothing left to do. A second build stage would delete both tools from the final image and
close most of the gap — the first exercise in the "What minimal costs" table in
[../README.md](../README.md).

## State

The watch list is `services.json` on disk, so anything added through the UI is lost when
the container is removed. The compose file bind-mounts that one file back to the host as
a stopgap. `services.py`'s own docstring explains why the real answer is a database.

## Inherited clutter

`bandit_demo/`, `mypy_demo/`, `conflict/`, `test_env/`, `notes.md`, `transcript.md`,
`pyproject.reference.toml` and a stray `uv.lock` came along with the copy and belong to
the module01 packaging lecture. All are listed in `.dockerignore`, so `COPY . .` never
sees them:

```bash
docker run --rm statusboard-poetry ls /app
```
