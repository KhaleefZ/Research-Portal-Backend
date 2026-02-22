from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, UploadFile

# Define allowed origins for your React frontend (Vercel/Netlify)
ALLOWED_ORIGINS = ["*"]  # In production, replace with your actual frontend URL

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def validate_file_type(file: UploadFile):
    """Ensures only PDFs are uploaded for processing."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF documents are supported.")
    return True