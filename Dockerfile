FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md alembic.ini ./
COPY alembic ./alembic
COPY src ./src

RUN pip install --upgrade pip
RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn meeting_intel.api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]