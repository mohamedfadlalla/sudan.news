# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY shared_models/ ./shared_models/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/
COPY news_bias.json ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash api
RUN chown -R api:api /app
USER api

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["gunicorn", "--config", "gunicorn.conf.py", "src.app:app"]
