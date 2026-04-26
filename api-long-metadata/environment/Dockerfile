FROM python:3.10-slim

RUN pip install --no-cache-dir \
    fastapi==0.115.5 \
    uvicorn[standard]==0.32.1 \
    PyPDF2==3.0.1 \
    python-multipart==0.0.20

WORKDIR /app/workspace
