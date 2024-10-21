# Base image with necessary build tools
FROM ubuntu:22.04 as base

# Install Python 3.10 and common dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip \
    libffi-dev \
    libssl-dev \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Builder stage
FROM base as builder

WORKDIR /app

# Copy application files and requirements.txt into the container
COPY --chmod=0755 --chown=0:0 face_model/ /app/face_model/
COPY --chmod=0755 --chown=0:0 requirements.txt /app/

# Create a virtual environment and install dependencies
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base

VOLUME [ "/app" ]
WORKDIR /app
# Copy virtual environment from builder stage
COPY --from=builder /app/venv /app/venv
COPY --chmod=0755 --chown=0:0 face_model/ /app/face_model

# Ensure the virtual environment is used
ENV PATH="/app/venv/bin:$PATH"

# Expose the application port
# HTTP PORT
EXPOSE 5000
# HTTPS PORT
EXPOSE 5443

# Run the application
CMD ["python", "/app/face_model/main.py"]
