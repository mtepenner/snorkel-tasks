FROM ubuntu:22.04

# Install C++ build tools and python for pytest
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

WORKDIR /app/workspace