import os
import json
import logging
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from aio_pika import connect, Message, DeliveryMode

from shared.models import Job
from api_service.database import get_db, init_db
from api_service.schemas import JobSubmitRequest, JobResponse, JobStatusResponse

# Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
QUEUE_NAME = "image_processing_queue"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# RabbitMQ Connection
rabbitmq_connection = None

@app.on_event("startup")
async def startup():
    await init_db()
    global rabbitmq_connection
    try:
        rabbitmq_connection = await connect(
            f"amqp://guest:guest@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
        )
        logger.info("Connected to RabbitMQ")
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")

@app.on_event("shutdown")
async def shutdown():
    if rabbitmq_connection:
        await rabbitmq_connection.close()

@app.post("/api/v1/images/process", response_model=JobResponse, status_code=202)
async def submit_job(request: JobSubmitRequest, db: AsyncSession = Depends(get_db)):
    # Create Job in DB
    new_job = Job(
        image_url=str(request.imageUrl),
        transformations=request.transformations,
        status="PENDING"
    )
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    # Publish to RabbitMQ
    if not rabbitmq_connection:
        raise HTTPException(status_code=500, detail="Messaging service unavailable")
    
    async with rabbitmq_connection.channel() as channel:
        message_body = json.dumps({
            "job_id": str(new_job.job_id),
            "image_url": str(new_job.image_url),
            "transformations": new_job.transformations
        }).encode()
        
        await channel.default_exchange.publish(
            Message(
                body=message_body,
                delivery_mode=DeliveryMode.PERSISTENT
            ),
            routing_key=QUEUE_NAME
        )

    return JobResponse(jobId=new_job.job_id)

@app.get("/api/v1/images/jobs/{jobId}", response_model=JobStatusResponse)
async def get_job_status(jobId: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Job).where(Job.job_id == jobId))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobStatusResponse(
            jobId=job.job_id,
            status=job.status,
            resultUrl=job.result_url,
            errorMessage=job.error_message
        )
    except Exception as e:
        logger.error(f"Error retrieving job {jobId}: {e}")
        # Validate UUID format in jobId if needed, otherwise 404 or 400
        raise HTTPException(status_code=404, detail="Job not found")

@app.get("/health")
def health_check():
    return {"status": "ok"}
