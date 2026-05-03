FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y default-jdk && rm -rf /var/lib/apt/lists/*

WORKDIR /app/workspace

RUN mkdir -p src data
