FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app/workspace

COPY src/ /app/workspace/src/

RUN pip install --no-cache-dir \
    flask==3.0.0 \
    pandas==2.1.4 \
    scikit-learn==1.3.2 \
    numpy==1.26.4 \
    werkzeug==3.0.1

CMD ["tail", "-f", "/dev/null"]