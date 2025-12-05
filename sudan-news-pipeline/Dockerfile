# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PyTorch and other ML libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY shared_models/ ./shared_models/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy pipeline source code
COPY config.py .
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash pipeline
RUN chown -R pipeline:pipeline /app
USER pipeline

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///data/news_aggregator.db

# Create data directory
RUN mkdir -p /app/data

# Expose any ports if needed (none for pipeline)
# EXPOSE

# Default command
CMD ["python", "-m", "src.run_pipeline", "run-once"]

# Optional: GPU support (uncomment if using GPU)
# FROM pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime
# (Then copy the rest of the instructions)
