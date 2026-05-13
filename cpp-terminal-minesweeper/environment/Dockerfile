FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

# Install runtime/build dependencies (test-only Python packages are installed in tests/test.sh)
RUN apt-get update && apt-get install -y \
    golang-go \
    g++ \
    make \
    curl \
    libcurl4-openssl-dev \
    imagemagick \
    libmagick++-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Setup directories
WORKDIR /app
RUN mkdir -p /app/workspace/src /app/workspace/data/replays /app/server

# Build the mock Gin server
COPY server.go /app/server/
RUN cd /app/server && go mod init api && go get github.com/gin-gonic/gin@v1.10.0 && go build -o backend server.go
