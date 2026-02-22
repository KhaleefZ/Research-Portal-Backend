#!/usr/bin/env python3
"""Quick test of the improved financial extraction."""

import sys
import os
sys.path.insert(0, "/Users/khaleef/Downloads/Assignment /Reserach-Tool/research-portal-backend")
os.chdir("/Users/khaleef/Downloads/Assignment /Reserach-Tool/research-portal-backend")

from app.services.pdf_processor import extract_text_from_pdf
from app.services.research_tool import run_financial_extraction
from app.services.excel_exporter import generate_excel_file

pdfs = {
    "Dabur": "../Dabur Quaterly Financial Statements.pdf",
    "Tata Motors": "../Tata Motors Quarterly Financial Statements.pdf"
}

print("\n" + "="*80)
print("TESTING IMPROVED FINANCIAL EXTRACTION")
print("="*80)

for company, pdf_path in pdfs.items():
    try:
        print(f"\n\n{'='*80}")
        print(f"Company: {company}")
        print(f"{'='*80}")
        
        # Step 1: Extract text
        print(f"\n✓ Reading PDF and extracting text...")
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        text = extract_text_from_pdf(pdf_bytes)
        if text.startswith("ERROR") or text.startswith("WARNING"):
            print(f"  ⚠️  {text[:100]}")
            continue
        
        text_len = len(text)
        print(f"  ✓ Extracted {text_len} characters")
        
        # Step 2: Extract financial data
        print(f"\n✓ Extracting financial metrics...")
        print(f"  (Using hybrid: local regex + Gemini fallback)")
        
        financial_data = run_financial_extraction(text)
        
        if not financial_data:
            print(f"  ⚠️  No financial data extracted")
        else:
            print(f"  ✓ Found {len(financial_data)} financial records")
            print(f"\n  Sample records:")
            for i, record in enumerate(financial_data[:5], 1):
                print(f"    {i}. {record['line_item']}: {record['value']:,.0f} {record['unit']}")
            if len(financial_data) > 5:
                print(f"    ... and {len(financial_data)-5} more")
        
        # Step 3: Generate Excel
        print(f"\n✓ Generating Excel file...")
        excel_buffer = generate_excel_file(financial_data)
        
        output_file = f"test_output_{company.replace(' ', '_')}.xlsx"
        with open(output_file, 'wb') as f:
            f.write(excel_buffer.getvalue())
        
        print(f"  ✓ Saved to: {output_file}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n\n{'='*80}")
print("Test completed!")
print(f"{'='*80}\n")
