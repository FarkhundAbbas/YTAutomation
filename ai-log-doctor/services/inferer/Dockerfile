FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc postgresql-client && rm -rf /var/lib/apt/lists/*
RUN pip install poetry

COPY pyproject.toml ./
COPY services/shared ./services/shared
COPY services/inferer ./services/inferer

RUN poetry config virtualenvs.create false && poetry install --no-root

EXPOSE 8003

CMD ["python", "-m", "services.inferer.main"]
