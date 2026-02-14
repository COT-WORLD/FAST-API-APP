FROM python:3.12.1 AS builder

WORKDIR /usr/src/app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.in-project true && \
    poetry install --no-root --no-interaction

FROM python:3.12.1-slim

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/.venv ./.venv

COPY . .

ENV PATH="/usr/src/app/.venv/bin:$PATH"

CMD ["uvicorn", "Fastpost.main:app", "--host", "0.0.0.0", "--port", "8000"]