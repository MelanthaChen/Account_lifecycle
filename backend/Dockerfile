FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN addgroup --system app && adduser --system --ingroup app app

COPY pyproject.toml ./

RUN pip install --upgrade pip setuptools wheel

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
COPY docker-entrypoint.sh ./docker-entrypoint.sh

RUN pip install . \
    && chmod +x /app/docker-entrypoint.sh \
    && chown -R app:app /app

USER app
EXPOSE 8000

CMD ["/app/docker-entrypoint.sh"]
