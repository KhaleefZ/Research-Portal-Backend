#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, "/Users/khaleef/Downloads/Assignment /Reserach-Tool/research-portal-backend")
os.chdir("/Users/khaleef/Downloads/Assignment /Reserach-Tool/research-portal-backend")

from app.services.pdf_processor import extract_text_from_pdf

pdfs = {
    "Dabur Quaterly Financial Statements.pdf": "../Dabur Quaterly Financial Statements.pdf",
    "Tata Motors Quarterly Financial Statements.pdf": "../Tata Motors Quarterly Financial Statements.pdf"
}

for name, pdf_path in pdfs.items():
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        extracted = extract_text_from_pdf(pdf_bytes)
        
        print(f"\n{'='*70}")
        print(f"File: {name}")
        print(f"{'='*70}")
        
        if extracted.startswith("ERROR") or extracted.startswith("WARNING"):
            print(f"⚠️  {extracted[:200]}")
        else:
            lines = extracted.count('\n')
            print(f"✓ Extracted {len(extracted)} characters")
            print(f"✓ {lines} lines extracted")
            print(f"\nFirst 500 characters of extracted text:")
            print("-"*70)
            print(extracted[:500])
            print("-"*70)
            
            # Check if financial keywords are present
            keywords = ['revenue', 'profit', 'income', 'financial', 'balance', 'statement']
            found = [kw for kw in keywords if kw.lower() in extracted.lower()]
            if found:
                print(f"✓ Financial keywords found: {', '.join(found)}")
            
    except Exception as e:
        print(f"Error processing {name}: {e}")
        import traceback
        traceback.print_exc()
