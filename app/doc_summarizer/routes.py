from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Path
from botocore.exceptions import NoCredentialsError
from datetime import datetime
from sqlalchemy.orm import Session
import boto3
from openai import OpenAI
import json
from uuid import UUID
from app.core.db import get_db
from app.core.config import get_settings, logger
from .models import DocumentBase
from .schemas import DocumentUploadResponse, AnalysisResponse, DocumentResponse
from .utils import extract_docx_text, extract_pdf_text



router = APIRouter()
config = get_settings()

s3_client = boto3.client(
        's3',
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
    )


openrouter_client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=config.OPENROUTER_API_KEY,
)



async def s3_bucket_upload(s3_key, content):
    try:
        s3_client.put_object(Bucket=config.S3_BUCKET, Key=s3_key, Body=content)
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="S3 credentials not configured.")
    
   

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.content_type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")
    
    logger.info("Uploaded file", file=file)
    # Check file size (max 5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit.")
    
    # Store in S3 
    file_name = file.filename
    s3_key = f"documents/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_name}"
    await s3_bucket_upload(s3_key, content)
 
    # Extract text
    extracted_text = ""
    if file.content_type == "application/pdf":
        extracted_text = extract_pdf_text(content)
        file_type = "pdf"
    else:  # DOCX
        extracted_text = extract_docx_text(content)
        file_type = "docx"
    logger.info("Text extracted", extracted_text=extracted_text)

    # Save to DB
    db_doc = DocumentBase(
        file_name=file_name,
        file_type=file_type,
        s3_key=s3_key,
        extracted_text=extracted_text
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    return DocumentUploadResponse(
        id=db_doc.id,
        file_name=file_name,
        s3_key=s3_key,
        message="Document uploaded and text extracted successfully."
    )



@router.post("/documents/{doc_id}/analyze", response_model=AnalysisResponse)
async def analyze_document(
    doc_id: UUID = Path(..., description="Document ID"),
    db: Session = Depends(get_db)
):
    # Fetch document
    db_doc = db.query(DocumentBase).filter(DocumentBase.id == str(doc_id)).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    if db_doc.summary:  # Already analyzed
        raise HTTPException(status_code=400, detail="Document already analyzed.")
    
    extracted_text = db_doc.extracted_text
    
    # Prompt for LLM 
    system_prompt = """
            You are an advanced document-analysis AI.  
            Your job is to read any provided document text and produce:
            1. A concise 2-3 sentence summary.
            2. The most likely document type (e.g., invoice, CV/resume, report, letter).
            3. Structured metadata extracted from the document (e.g., dates, names, sender, totals).  
            If a metadata field cannot be determined, set it to null.

            You must ALWAYS respond strictly in valid JSON format:
            {
                "summary": "",
                "doc_type": "",
                "metadata": {}
            }
        """
    user_prompt = f"""
            Analyze the following document text and provide:

            1. A concise summary (2–3 sentences).
            2. The detected document type.
            3. Extracted metadata as key-value pairs (use null if a field cannot be determined).

            Document text:
            {extracted_text[:4000]}

            Respond in valid JSON:
            {{
                "summary": "Your summary here",
                "doc_type": "Detected type",
                "metadata": {{"key1": "value1", "key2": "value2"}}
            }}
        """
    try:
        chat_completion = openrouter_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            )
        llm_response = chat_completion.choices[0].message.content
        logger.info("llm response", llm_response=llm_response)

        # Parse JSON response 
        parsed = json.loads(llm_response)
        summary = parsed.get("summary", "")
        doc_type = parsed.get("doc_type", "")
        metadata = parsed.get("metadata", {})
        
        # Save to DB
        db_doc.summary = summary
        db_doc.doc_type = doc_type
        db_doc.doc_metadata = metadata
        db.commit()
        
        return AnalysisResponse(
            id=doc_id,
            summary=summary,
            doc_type=doc_type,
            metadata=metadata,
            message="Analysis completed successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: UUID = Path(..., description="Document ID"),
    db: Session = Depends(get_db)
):
    db_doc = db.query(DocumentBase).filter(DocumentBase.id == str(doc_id)).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    return DocumentResponse(
        id=db_doc.id,
        file_name=db_doc.file_name,
        file_type=db_doc.file_type,
        s3_key=db_doc.s3_key,
        extracted_text=db_doc.extracted_text,
        upload_date=db_doc.upload_date,
        summary=db_doc.summary,
        doc_type=db_doc.doc_type,
        metadata=db_doc.doc_metadata
    )
