# environment/Dockerfile
FROM python:3.10-slim

# Install system utilities and Python dependencies required for the task
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install FastAPI, Uvicorn (server), PyPDF2 (parsing), and python-multipart (file uploads)
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    PyPDF2 \
    python-multipart

# Set the working directory to the Snorkel platform standard
WORKDIR /app/workspace

# Note: The agent will populate the actual code here during the run.
