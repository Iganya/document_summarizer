from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class DocumentUploadResponse(BaseModel):
    id: UUID
    file_name: str
    s3_key: str
    message: str

class AnalysisResponse(BaseModel):
    id: UUID
    summary: str
    doc_type: str
    metadata: dict
    message: str

class DocumentResponse(BaseModel):
    id: UUID
    file_name: str
    file_type: str
    s3_key: str
    extracted_text: str
    upload_date: datetime
    summary: Optional[str]
    doc_type: Optional[str]
    metadata: Optional[dict]