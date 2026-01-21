FROM python:3.11-slim

WORKDIR /app

# Upgrade pip and increase timeout
ENV PIP_DEFAULT_TIMEOUT=100
RUN pip install --upgrade pip

COPY worker-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module
COPY shared /app/shared

# Copy Worker service code
COPY worker-service /app/worker_service

# Run worker
CMD ["python", "-m", "worker_service.worker"]
