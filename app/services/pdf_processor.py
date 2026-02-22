import fitz  # PyMuPDF (pip install pymupdf)
import logging
import io
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text from PDFs using hybrid approach: text extraction + OCR fallback.
    
    Handles both:
    1. Text-based PDFs (extracts directly)
    2. Image-based PDFs (uses Tesseract OCR)
    
    Args:
        pdf_bytes: Raw PDF file bytes
        
    Returns:
        Extracted text with page markers
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_content = []
        pages_analyzed = 0
        
        for i, page in enumerate(doc):
            # STEP 1: Try direct text extraction first (fast for text-based PDFs)
            blocks = page.get_text("blocks")
            blocks.sort(key=lambda b: (b[1], b[0]))  # Sort by position
            text_content = "\n".join([b[4].strip() for b in blocks if b[4].strip()])
            
            # If we got meaningful text, use it
            if text_content.strip() and len(text_content.strip()) > 50:
                full_content.append(f"--- START OF PAGE {i+1} ---\n{text_content.strip()}\n--- END OF PAGE {i+1} ---")
                pages_analyzed += 1
                continue
            
            # STEP 2: If no text found, assume image-based PDF and use OCR
            logger.info(f"Page {i+1}: No direct text. Attempting OCR...")
            
            try:
                # Convert PDF page to image and apply OCR
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)  # 2x zoom for better OCR
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Use Tesseract OCR with optimized settings
                ocr_text = pytesseract.image_to_string(
                    image,
                    config='--psm 1'  # PSM 1: auto page segmentation with OSD
                )
                
                if ocr_text.strip():
                    logger.info(f"Page {i+1}: OCR extracted {len(ocr_text)} characters")
                    full_content.append(f"--- START OF PAGE {i+1} [OCR] ---\n{ocr_text.strip()}\n--- END OF PAGE {i+1} ---")
                    pages_analyzed += 1
                else:
                    logger.warning(f"Page {i+1}: OCR returned empty text")
                    
            except pytesseract.TesseractNotFoundError as e:
                logger.error(f"Tesseract not installed: {str(e)}")
                return f"ERROR: OCR library (Tesseract) not found. Install with: brew install tesseract"
            except Exception as ocr_error:
                logger.error(f"Page {i+1} OCR failed: {str(ocr_error)}")
                continue
        
        if not full_content:
            error_msg = f"No readable text found in {len(doc)} pages. All pages appear to be empty images."
            logger.warning(error_msg)
            return f"WARNING: {error_msg}"
        
        # Log extraction success
        logger.info(f"Successfully processed {pages_analyzed}/{len(doc)} pages")
        return "\n\n".join(full_content)
        
    except Exception as e:
        error_msg = f"PDF Extraction Error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"ERROR: {error_msg}"