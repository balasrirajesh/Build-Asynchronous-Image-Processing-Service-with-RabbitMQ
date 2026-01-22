import os
import asyncio
import json
import logging
import aio_pika
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update, select

# Adjust python path if needed in Docker, but shared/ should be in path
from shared.models import Job
from worker_service.processor import ImageProcessor

# Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "image_processor_db")
PROCESSED_IMAGES_DIR = os.getenv("PROCESSED_IMAGES_DIR", "processed_images")

QUEUE_NAME = "image_processing_queue"
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Setup
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

image_processor = ImageProcessor(PROCESSED_IMAGES_DIR)

async def update_job_status(job_id, status, result_url=None, error_message=None):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = update(Job).where(Job.job_id == job_id).values(
                status=status,
                result_url=result_url,
                error_message=error_message
            )
            await session.execute(stmt)

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        data = json.loads(message.body)
        job_id = data.get("job_id")
        image_url = data.get("image_url")
        transformations = data.get("transformations", [])
        
        logger.info(f"Processing job {job_id}")

        # Idempotency Check
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Job).where(Job.job_id == job_id))
            existing_job = result.scalar_one_or_none()
            if existing_job and existing_job.status == "COMPLETED":
                logger.info(f"Job {job_id} is already COMPLETED. Skipping processing to ensure idempotency.")
                return


        try:
            # Update status to PROCESSING
            await update_job_status(job_id, "PROCESSING")

            # Download
            image_data = await image_processor.download_image(image_url)

            # Process (CPU bound, run in thread pool if heavy, but for this demo sync is okay or use run_in_executor)
            loop = asyncio.get_running_loop()
            result_path = await loop.run_in_executor(None, image_processor.process_image, image_data, transformations, job_id)

            # Update status to COMPLETED
            await update_job_status(job_id, "COMPLETED", result_url=result_path)
            logger.info(f"Job {job_id} completed. Result: {result_path}")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            await update_job_status(job_id, "FAILED", error_message=str(e))

async def main():
    # Wait for DB? Docker depends_on handles startup order but sometimes DB needs more time.
    # Retry logic could be added here for robustness.
    
    connection = await aio_pika.connect_robust(
        f"amqp://guest:guest@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
    )

    channel = await connection.channel()
    
    # Declare queue to ensure it exists
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    await queue.consume(process_message)
    
    logger.info("Worker started, waiting for messages...")
    await asyncio.Future() # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
