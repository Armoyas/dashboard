# syntax=docker/dockerfile:1

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY ./api /app/api

# Copy the database schema
COPY ../database/schema.sql /app/database/schema.sql
# Data files (data/*.csv) are mounted at runtime via docker-compose volume ./data:/app/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "from api.database.connection import get_connection; get_connection()"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]