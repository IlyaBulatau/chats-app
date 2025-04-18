FROM python:3.10.16-slim-bullseye as builder

ENV \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.8.0 \
    POETRY_HOME='/opt/local' \
    PATH="/opt/local/bin:$PATH"

WORKDIR $POETRY_HOME

COPY pyproject.toml ./

RUN apt-get update && apt-get install --no-install-recommends --no-install-suggests -y \
    gcc \
    python3-dev \
    libpq-dev \
    curl && \
    apt-get clean && \
    curl -sSL https://install.python-poetry.org | POETRY_VERSION=$POETRY_VERSION python3 - && \
    poetry install --no-ansi --only main && \
    apt-get purge -y gcc python3-dev libpq-dev curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    poetry cache clear --all --no-interaction PyPI && \
    poetry cache clear --all --no-interaction _default_cache

# ---------------------------------------------------------------------------
# development stage
FROM builder as development

COPY --from=builder $POETRY_HOME $POETRY_HOME

WORKDIR $POETRY_HOME

RUN poetry install --no-ansi --only dev

WORKDIR /home/app

COPY ./chat .

# ---------------------------------------------------------------------------
# test stage
FROM builder as test

COPY --from=builder $POETRY_HOME $POETRY_HOME

WORKDIR $POETRY_HOME

RUN poetry install --no-ansi --only test

WORKDIR /home/app

COPY ./chat .

# ---------------------------------------------------------------------------
# production stage
FROM builder as production

COPY --from=builder $POETRY_HOME $POETRY_HOME

WORKDIR /home/app

COPY ./chat .

COPY entrypoint.sh .

RUN chmod +x ./entrypoint.sh

RUN groupadd -r app && \
    useradd -r -g app app && \
    chown -R app:app /home/app

USER app

ENTRYPOINT [ "./entrypoint.sh" ]