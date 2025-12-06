from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.db import Base
from uuid import uuid4


class DocumentBase(Base):
    __tablename__ = "documents"
    id = Column(String(255), primary_key=True, default=lambda: str(uuid4()), nullable=False, index=True)
    file_name = Column(String(255), index=True)
    file_type = Column(String(255))
    s3_key = Column(String(255))
    extracted_text = Column(Text)
    upload_date = Column(DateTime, default=func.now())
    summary = Column(Text)
    doc_type = Column(String(255))
    doc_metadata = Column(JSON)