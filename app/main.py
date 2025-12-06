from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from .doc_summarizer import routes
from fastapi.exceptions import RequestValidationError
from .core.db import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Document Summarization Service")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  # Or another status code
        content={"error": "Validation failed"},
        )
app.include_router(routes.router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)