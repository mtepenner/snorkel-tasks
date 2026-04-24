FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app/workspace

RUN pip install --no-cache-dir \
    flask \
    pandas \
    scikit-learn \
    numpy \
    pytest \
    pytest-flask \
    requests \
    werkzeug

CMD ["tail", "-f", "/dev/null"]