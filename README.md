# Asynchronous Image Processing Service

A scalable, microservices-based system for asynchronous image processing using FastAPI, RabbitMQ, PostgreSQL, and Docker.

## Features
- **Asynchronous Processing**: Offloads image transformations to background workers.
- **Scalable Architecture**: Decoupled API and Worker services via RabbitMQ.
- **Reliable**: Implements message persistence and acknowledgements.
- **Idempotent**: Worker handles duplicate messages gracefully.
- **Dockerized**: specific `docker-compose.yml` for easy deployment.

## Architecture
- **API Service**: FastAPI application that accepts jobs, validates input, stores initial status in DB, and publishes messages to RabbitMQ.
- **Worker Service**: Python-based worker consuming from RabbitMQ. Downloads images, applies transformations (Resize, Grayscale), saves to disk, and updates DB status.
- **RabbitMQ**: Message broker for task distribution.
- **PostgreSQL**: Persistent storage for job metadata.
- **Shared Volume**: Stores processed images.

## Setup & Installation

### Prerequisites
- Docker & Docker Compose

### Running the Application
1. **Clone the repository** (if applicable).
2. **Navigate to the project root**.
3. **Run with Docker Compose**:
    ```bash
    docker-compose up --build
    ```
4. **Access the API**:
    - Health Check: `http://localhost:8000/health`
    - Submit Job: `POST http://localhost:8000/api/v1/images/process`
    - Check Status: `GET http://localhost:8000/api/v1/images/jobs/{jobId}`

## API Documentation

### POST /api/v1/images/process
Submit a new image processing job.

**Request Body:**
```json
{
  "imageUrl": "https://example.com/image.jpg",
  "transformations": ["resize:100x100", "grayscale"]
}
```

**Response (202 Accepted):**
```json
{
  "jobId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

### GET /api/v1/images/jobs/{jobId}
Get the status of a job.

**Response (200 OK):**
```json
{
  "jobId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "COMPLETED",
  "resultUrl": "/app/processed_images/3fa85f64-5717-4562-b3fc-2c963f66afa6.png",
  "errorMessage": null
}
```

## Running Tests
Tests are located in the `tests/` directory and can be run inside the containers.

**Run API Unit & Integration Tests:**
```bash
docker-compose exec api-service pytest /app/tests/test_api.py /app/tests/test_integration.py
```

**Run Worker Unit Tests:**
```bash
docker-compose exec worker-service pytest /app/tests/test_processor.py
```

## Design Decisions
- **Shared Code**: Database models are shared to ensure consistency.
- **Idempotency**: The worker regenerates the image if the job is re-processed. Since transformations are deterministic, this allows safe retries without side effects (other than wasted CPU).
- **Error Handling**: Failed downloads or processing update the job status to `FAILED` with an error message.
