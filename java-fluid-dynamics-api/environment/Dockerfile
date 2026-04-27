FROM python:3.13

RUN apt-get update && apt-get install -y openjdk-17-jdk curl && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app/workspace

RUN mkdir -p src data
