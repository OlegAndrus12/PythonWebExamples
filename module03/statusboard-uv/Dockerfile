# The smallest Dockerfile that runs this app. Five instructions.
#
# The base image is Python 3.12 with the uv binary already in it, so there is
# nothing to install before installing dependencies.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# .dockerignore decides what this actually copies.
COPY . .

# --frozen  install exactly what uv.lock says, or fail. No re-resolving.
# --no-dev  skip pytest/ruff/bandit/pre-commit; they are not needed to serve.
RUN uv sync --frozen --no-dev

# --host 0.0.0.0 is required: Flask's default 127.0.0.1 binds only the
# container's own loopback, so a published port would reach nothing.
CMD ["/app/.venv/bin/flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "8000"]
