FROM python:3.10-slim

WORKDIR /app/workspace

COPY src/ /app/workspace/src/

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

CMD ["tail", "-f", "/dev/null"]