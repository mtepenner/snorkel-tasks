FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    ruby-full \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY puzzles.json /app/puzzles.json
