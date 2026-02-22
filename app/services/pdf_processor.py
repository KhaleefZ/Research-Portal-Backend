import fitz  # PyMuPDF (pip install pymupdf)
import logging
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts text from PDFs using hybrid approach:
    1. Direct text extraction
    2. OCR fallback (Tesseract)

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
            # -------- Direct Text Extraction --------
            blocks = page.get_text("blocks")
            blocks.sort(key=lambda b: (b[1], b[0]))
            text_content = "\n".join(
                [b[4].strip() for b in blocks if b[4].strip()]
            )

            # -------- OCR Extraction --------
            ocr_text = ""
            try:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples
                )
                ocr_text = pytesseract.image_to_string(
                    image,
                    config="--psm 1"
                )
            except pytesseract.TesseractNotFoundError:
                logger.error("Tesseract not installed. Install with: brew install tesseract")
            except Exception as e:
                logger.error(f"OCR failed on page {i+1}: {str(e)}")

            # -------- Combine Text --------
            combined_text = text_content.strip()

            if ocr_text.strip():
                if not combined_text or len(combined_text) < 50:
                    combined_text += "\n" + ocr_text.strip()
                else:
                    combined_text += "\n" + ocr_text.strip()

            if combined_text.strip():
                full_content.append(
                    f"--- START OF PAGE {i+1} ---\n"
                    f"{combined_text}\n"
                    f"--- END OF PAGE {i+1} ---"
                )
                pages_analyzed += 1
            else:
                logger.warning(f"Page {i+1}: No text found.")

        if not full_content:
            logger.warning("No readable text found in the document.")
            return "WARNING: No readable text found in PDF."

        logger.info(f"Successfully processed {pages_analyzed}/{len(doc)} pages")
        return "\n\n".join(full_content)

    except Exception as e:
        logger.error("PDF Extraction Error", exc_info=True)
        return f"ERROR: PDF Extraction Error: {str(e)}"
