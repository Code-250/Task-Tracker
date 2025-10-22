# Multi-stage Dockerfile for QR Code Service
# Build stage
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app/ /app/app/

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV TEAM_NAME=Cumulonimbus
ENV TEAM_AWS_ID=587764054854
ENV AUTH_SERVICE_URL=http://auth-service:9000

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
