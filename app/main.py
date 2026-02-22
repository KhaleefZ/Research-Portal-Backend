from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
import io

# Internal imports
from app.core.config import settings
from app.core.security import setup_cors, validate_file_type
from app.services.pdf_processor import extract_text_from_pdf
from app.services.research_tool import run_financial_extraction
from app.services.excel_exporter import generate_excel_file

# Initialize FastAPI app
app = FastAPI(title=settings.PROJECT_NAME)

# Apply CORS middleware for React frontend connectivity
setup_cors(app)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "online", "tool": "Financial Statement Extractor"}

@app.post("/api/research/extract-financials")
async def extract_financials(file: UploadFile = File(...)):
    """
    Main endpoint for the Research Tool (Option A).
    Flow: Ingest -> Parse -> Extract (LLM) -> Format (Excel)
    """
    # 1. Security & Validation [cite: 52]
    validate_file_type(file)
    
    try:
        # 2. Ingestion: Read and parse the document [cite: 8, 60]
        pdf_bytes = await file.read()
        raw_text = extract_text_from_pdf(pdf_bytes)
        
        # Check for extraction errors
        if raw_text.startswith("ERROR") or raw_text.startswith("WARNING"):
            debug_info = raw_text  # Include extraction issue as debug info
        else:
            debug_info = None

        # 3. Research Tool Execution: LLM Extraction [cite: 9, 61]
        # This handles judgment calls like currency and line item mapping [cite: 17, 19]
        extracted_data = run_financial_extraction(raw_text)

        # 4. Structured Output: Generate the Excel file 
        # Ready for analyst calculations and verification [cite: 63]
        # Pass debug_info if extraction had issues
        excel_buffer = generate_excel_file(extracted_data, debug_info=debug_info)

        # 5. Return the file as a downloadable stream [cite: 50]
        filename = f"research_extract_{file.filename.split('.')[0]}.xlsx"
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        # Reliability: Provide clear error feedback [cite: 54, 56]
        import logging
        logging.error(f"Extraction pipeline error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)