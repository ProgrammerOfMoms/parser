FROM python:3.10-slim as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.4.1

RUN apt-get update && apt-get install -y gcc libffi-dev musl-dev libpq-dev
RUN pip install poetry==1.4.1

COPY pyproject.toml poetry.lock ./
RUN poetry export --dev -f requirements.txt | pip install -r /dev/stdin

COPY . .

RUN poetry build