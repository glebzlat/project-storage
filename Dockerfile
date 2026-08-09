# syntax=docker/dockerfile:1

FROM python:3.14.6-alpine3.23 AS builder

ENV PYTHONUNBUFFERED=1 \
    \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR="/tmp/.poetry" \
    POETRY_HOME="/home/runner/poetry"

RUN adduser -D runner && \
    mkdir -p /home/runner/app && \
    chown runner:runner /home/runner/app
WORKDIR /home/runner/app
USER runner

RUN python3 -m venv "$POETRY_HOME" && \
    $POETRY_HOME/bin/pip install poetry==2.4.1

COPY pyproject.toml poetry.lock ./

RUN $POETRY_HOME/bin/poetry install --no-root


FROM python:3.14.6-alpine3.23 AS runner

EXPOSE 8000

RUN adduser -D runner && \
    mkdir -p /home/runner/app && \
    chown runner:runner /home/runner/app
WORKDIR /home/runner/app
USER runner

ENV VIRTUAL_ENV=.venv \
    PATH=/home/runner/app/.venv/bin:$PATH

COPY --from=builder /home/runner/app/$VIRTUAL_ENV $VIRTUAL_ENV

COPY --parents --chown=app:app alembic.ini src ./

ENTRYPOINT ["fastapi"]
