FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y curl build-essential libpq-dev

# Setup working directory
WORKDIR /app

# Install Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY . .

# Disable virtualenv creation in Docker
ENV POETRY_VIRTUALENVS_CREATE=false

# Install deps
RUN poetry install --no-interaction --no-ansi

# Run the server
CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "movierama.wsgi:application"]
