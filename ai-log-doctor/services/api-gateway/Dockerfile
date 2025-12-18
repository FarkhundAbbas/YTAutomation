FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml ./
COPY services/shared ./services/shared
COPY services/api-gateway ./services/api-gateway
COPY scripts ./scripts

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-root

EXPOSE 8000

CMD ["python", "-m", "services.api-gateway.main"]
