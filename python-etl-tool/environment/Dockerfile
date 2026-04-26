FROM python:3.13-slim-bookworm

WORKDIR /app

# Install system dependencies required for the agent/debugging
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir Flask