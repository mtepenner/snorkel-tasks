FROM python:3.10-slim

# Install system dependencies for Graphviz
RUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with pinned versions (Removed pytest)
RUN pip install "numpy<2.0.0" pandas==2.0.3 graphviz==0.20.1

# Setup workspace
WORKDIR /app/workspace
RUN mkdir -p data src output

# Seed the raw data for testing using printf for correct newline parsing
RUN printf 'region_id,year,temperature\n1,2020,14.5\n1,2021,15.0\n2,2020,22.1\n2,2021,22.5\n' > data/climate.csv
RUN echo '{"1": "North America", "2": "Europe"}' > data/metadata.json

# Default command
CMD ["/bin/bash"]