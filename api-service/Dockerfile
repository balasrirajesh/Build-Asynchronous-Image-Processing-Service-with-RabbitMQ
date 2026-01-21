FROM python:3.11-slim

WORKDIR /app

# Upgrade pip and increase timeout
ENV PIP_DEFAULT_TIMEOUT=100
RUN pip install --upgrade pip

COPY api-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module
COPY shared /app/shared

# Copy API service code
COPY api-service /app/api_service

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "api_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
