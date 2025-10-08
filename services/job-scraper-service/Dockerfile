FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --no-root

COPY src/ src/
COPY models/ models/

EXPOSE 8002
CMD ["poetry", "run", "uvicorn", "src.job_scraper_service.main:app", "--host", "0.0.0.0", "--port", "8002"]