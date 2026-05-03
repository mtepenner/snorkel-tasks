FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends g++ && rm -rf /var/lib/apt/lists/*

WORKDIR /app/workspace

RUN mkdir -p /app/workspace/src
COPY src/ /app/workspace/src/
