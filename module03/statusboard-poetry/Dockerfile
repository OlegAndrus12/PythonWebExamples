# The smallest Dockerfile that runs this app with Poetry. Six instructions —
# one more than ../statusboard-uv/Dockerfile, and the extra one is the point.
#
# There is no official Poetry base image, so Poetry has to be installed before
# it can install anything else.
FROM python:3.12-slim-bookworm

# Poetry's default is a virtualenv under ~/.cache/pypoetry/virtualenvs, named
# after a hash of the project path — awkward to reference from CMD. This puts
# it at a predictable /app/.venv instead, exactly where uv would have put it.
#
# The tempting alternative, POETRY_VIRTUALENVS_CREATE=false, installs into the
# image's system Python. Do not: Poetry itself lives there, so the app ends up
# sharing an environment with Poetry's ~40 dependencies and can silently run
# against *their* version of a package instead of the one poetry.lock pins.
# See the README — it is measurable, not theoretical.
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Version pinned to the one that generated poetry.lock. Unpinned, this line
# quietly changes what builds your image.
RUN pip install --no-cache-dir poetry==2.4.1

WORKDIR /app

# .dockerignore decides what this actually copies.
COPY . .

# --without dev  skip the [tool.poetry.group.dev] packages — ruff, pytest,
#                bandit, mypy, pre-commit. Nothing serves traffic.
#
# There is no --frozen flag to pass: Poetry refuses to install from a
# poetry.lock that no longer matches pyproject.toml, so a stale lock fails the
# build. `pyproject.toml` also sets package-mode = false, which is why this
# does not need --no-root.
RUN poetry install --without dev

# Identical to the uv build's CMD. `poetry run flask ...` would also work, but
# calling the venv's entry point directly keeps Poetry out of the runtime path.
#
# --host 0.0.0.0 is required: Flask's default 127.0.0.1 binds only the
# container's own loopback, so a published port would reach nothing.
CMD ["/app/.venv/bin/flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "8000"]
