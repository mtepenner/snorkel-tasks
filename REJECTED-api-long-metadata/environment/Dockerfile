FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jdk-headless \
    junit5 \
    libgoogle-gson-java \
    libpdfbox2-java \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/workspace

RUN mkdir -p /app/workspace/src/static
