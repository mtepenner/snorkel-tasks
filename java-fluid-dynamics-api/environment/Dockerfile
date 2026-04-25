FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y openjdk-17-jdk curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app/workspace

RUN mkdir -p src data