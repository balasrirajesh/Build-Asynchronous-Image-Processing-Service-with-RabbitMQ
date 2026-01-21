import uuid
from sqlalchemy import Column, String, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_url = Column(String(255), nullable=False)
    transformations = Column(JSON, nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")
    result_url = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
