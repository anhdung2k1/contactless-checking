# Base image with necessary build tools
FROM ubuntu:latest as base

# Install Python and common dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    libffi-dev \
    libssl-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Builder stage
FROM base as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application files and requirements.txt into the container
COPY face_model/* /app/
COPY requirements.txt /app/

# Create a virtual environment and install dependencies
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/venv /app/venv
COPY face_model/* /app/

# Ensure the virtual environment is used
ENV PATH="/app/venv/bin:$PATH"

# Expose the application port
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]
