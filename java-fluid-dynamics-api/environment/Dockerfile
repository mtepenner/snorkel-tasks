FROM python:3.13

RUN apt-get update && apt-get install -y openjdk-17-jdk && rm -rf /var/lib/apt/lists/*

WORKDIR /app/workspace

RUN mkdir -p src data
