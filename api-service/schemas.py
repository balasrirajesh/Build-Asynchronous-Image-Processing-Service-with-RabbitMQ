from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from uuid import UUID

class JobSubmitRequest(BaseModel):
    imageUrl: HttpUrl
    transformations: List[str]

class JobResponse(BaseModel):
    jobId: UUID

class JobStatusResponse(BaseModel):
    jobId: UUID
    status: str
    resultUrl: Optional[str] = None
    errorMessage: Optional[str] = None
