FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential \
        libpq-dev \
        postgresql-client

# Environment variables to configure Poetry
ENV POETRY_VERSION=2.1.4 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry


COPY poetry.lock pyproject.toml /app/

RUN poetry install --no-root --no-interaction --no-ansi --verbose

COPY . .

EXPOSE 8000

RUN chmod +x /app/run.sh

CMD ["sh", "./run.sh"]
