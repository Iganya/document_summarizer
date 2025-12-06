# 🧙 AI Document Summarization & Metadata Extraction API

## AI Document Summarization & Metadata Extraction API

FastAPI + Openrouter + S3 + MySQL
A production-ready service that accepts PDF or DOCX files, extracts text, stores them securely, and uses gpt-4o-min llm model on openrouter to generate:
- Concise summary (2–3 sentences)
- Document type classification (invoice, CV/resume, contract, report, letter, etc.)
- Structured metadata extraction (date, sender, recipient, total amount, invoice number, e
---

## 🚀 Endpoints

- POST /documents/upload: Upload PDF or DOCX (returns document ID)
- POST /documents/{id}/analyze: Trigger AI summarization & metadata extraction
- GET /documents/{id}: Get full document + AI results

## Example Workflow
### 1. Upload
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@invoice.pdf"
```
### 2. Analyze
```bash
curl -X POST "http://localhost:8000/documents/a7c0af3d-92b7-4e24-97bb-03d22005d3cf/analyze"
```

### 3. Retrieve everything
```bash
curl http://localhost:8000/documents/a7c0af3d-92b7-4e24-97bb-03d22005d3cf
```
### Sample response
```bash
{
  "id": a7c0af3d-92b7-4e24-97bb-03d22005d3cf,
  "file_name": "invoice.pdf",
  "summary": "Invoice from ACME Corp to John Doe for web development services totaling $4,250. Payment due by Dec 30, 2025.",
  "doc_type": "invoice",
  "metadata": {
    "invoice_number": "INV-2025-0421",
    "date": "2025-12-01",
    "sender": "ACME Corp",
    "recipient": "John Doe",
    "total_amount": 4250.00,
    "currency": "USD",
    "due_date": "2025-12-30"
   }
}
```

## Technology Stack
- Programming Language: Python
- Framework: FastAPI
- Database: Mysql


## How to Run Locally
1. Clone the repository:
   ```bash
   https://github.com/Iganya/document_summarizer.git
   cd your-repo
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI application:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
5. Access the API at `http://127.0.0.1:8000/`



## Environment Variables

Create a `.env` file in the project root and configure the following variables:

```env
# Database
MYSQL_USER=your_user_name
MYSQL_PASSWORD=your_password
MYSQL_HOST=your_hostname
MYSQL_PORT=your_mysql_port
MYSQL_DB=your_db_name
DATABASE_URL=mysql+pymysql://your_user_name:your_password@your_hostname:your_mysql_port/your_db_name


# Amazon S3 Configuration
S3_BUCKET=your_bucket_name
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# OpenRouter API
OPENROUTER_API_KEY=your_api_key
```

