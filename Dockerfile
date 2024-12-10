FROM python:3.10.16-slim-bullseye as builder

ENV \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME='/usr/local' \
    PATH="$HOME/.local/bin:$PATH"

RUN apt-get update && apt-get install --no-install-recommends --no-install-suggests -y \
    gcc \
    python3-dev \
    libpq-dev \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR $POETRY_HOME

COPY pyproject.toml ./

RUN poetry install --no-ansi --only main

# ---------------------------------------------------------------------------
# development stage
FROM builder as development

COPY --from=builder $POETRY_HOME $POETRY_HOME

WORKDIR $POETRY_HOME

RUN poetry install --no-ansi --only dev

WORKDIR /home/code

COPY ./chat .

# ---------------------------------------------------------------------------
# test stage
FROM builder as test

COPY --from=builder $POETRY_HOME $POETRY_HOME

WORKDIR $POETRY_HOME

RUN poetry install --no-ansi --only test

WORKDIR /home/code

COPY ./chat .

# ---------------------------------------------------------------------------
# production stage
FROM builder as production

COPY --from=builder $POETRY_HOME $POETRY_HOME

WORKDIR /home/code

RUN groupadd -r app && \
    useradd -r -g app app && \
    chown -R app:app /home/code

COPY ./chat .

COPY entrypoint.sh .

RUN chmod +x ./entrypoint.sh

USER app

ENTRYPOINT [ "./entrypoint.sh" ]