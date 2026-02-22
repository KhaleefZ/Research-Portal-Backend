#!/usr/bin/env python3
"""Test the complete financial extraction pipeline with OCR support."""

import sys
import os
sys.path.insert(0, "/Users/khaleef/Downloads/Assignment /Reserach-Tool/research-portal-backend")
os.chdir("/Users/khaleef/Downloads/Assignment /Reserach-Tool/research-portal-backend")

from app.services.pdf_processor import extract_text_from_pdf
from app.services.research_tool import run_financial_extraction
from app.services.excel_exporter import generate_excel_file

PDFs = {
    "Dabur": "../Dabur Quaterly Financial Statements.pdf",
    "Tata Motors": "../Tata Motors Quarterly Financial Statements.pdf"
}

print("\n" + "="*80)
print("COMPLETE FINANCIAL EXTRACTION PIPELINE TEST")
print("="*80)

for company, pdf_path in PDFs.items():
    print(f"\n\n{'='*80}")
    print(f"Testing: {company}")
    print(f"{'='*80}")
    
    try:
        # STEP 1: READ PDF
        print(f"\n[STEP 1] Reading PDF file...")
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        print(f"  ✓ Loaded {len(pdf_bytes)} bytes")
        
        # STEP 2: EXTRACT TEXT (WITH OCR IF NEEDED)
        print(f"\n[STEP 2] Extracting text from PDF...")
        extracted_text = extract_text_from_pdf(pdf_bytes)
        
        if extracted_text.startswith("ERROR"):
            print(f"  ✗ {extracted_text}")
            continue
        elif extracted_text.startswith("WARNING"):
            print(f"  ⚠️  {extracted_text}")
            continue
        else:
            text_length = len(extracted_text)
            lines = extracted_text.count('\n')
            has_ocr = "[OCR]" in extracted_text
            print(f"  ✓ Extracted {text_length} characters, {lines} lines")
            print(f"  {'✓' if has_ocr else '○'} OCR Used: {has_ocr}")
        
        # STEP 3: EXTRACT FINANCIAL DATA
        print(f"\n[STEP 3] Extracting financial data with Gemini AI...")
        financial_data = run_financial_extraction(extracted_text)
        
        if not financial_data:
            print(f"  ⚠️  No financial data extracted")
            print(f"  Note: This might indicate:")
            print(f"    - Document contains no financial statements")
            print(f"    - Financial data format not recognized")
            print(f"    - API rate limit or connection issue")
            financial_data = []
        else:
            print(f"  ✓ Extracted {len(financial_data)} financial records")
            print(f"\n  Sample records (first 3):")
            for i, record in enumerate(financial_data[:3], 1):
                print(f"    {i}. {record['line_item']}: {record['value']} {record['unit']} ({record['period']})")
        
        # STEP 4: GENERATE EXCEL
        print(f"\n[STEP 4] Generating Excel file...")
        excel_buffer = generate_excel_file(financial_data)
        print(f"  ✓ Excel file generated ({excel_buffer.getbuffer().nbytes} bytes)")
        
        # Save for manual inspection
        output_file = f"output_{company.replace(' ', '_')}.xlsx"
        with open(output_file, 'wb') as f:
            f.write(excel_buffer.getvalue())
        print(f"  ✓ Saved to: {output_file}")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n\n{'='*80}")
print("Pipeline test completed!")
print(f"{'='*80}\n")
