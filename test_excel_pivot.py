#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, "/Users/khaleef/Downloads/Assignment /Reserach-Tool/research-portal-backend")
os.chdir("/Users/khaleef/Downloads/Assignment /Reserach-Tool/research-portal-backend")

from app.services.pdf_processor import extract_text_from_pdf
from app.services.research_tool import run_financial_extraction
from app.services.excel_exporter import generate_excel_file
import pandas as pd

pdf_path = "../Dabur Quaterly Financial Statements.pdf"

print("\nTesting updated Excel export format...")
print("="*100)

try:
    # Read and extract
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    text = extract_text_from_pdf(pdf_bytes)
    financial_data = run_financial_extraction(text)
    
    print(f"✓ Extracted {len(financial_data)} financial records\n")
    
    # Show sample data structure
    if financial_data:
        print("Sample extracted data structure:")
        for i, rec in enumerate(financial_data[:5], 1):
            print(f"  {i}. {rec['line_item']:40s} = {rec['value']:10,.0f} {rec['unit']:10s} ({rec['period']})")
    
    print(f"\n✓ Generating Excel with pivot table format...")
    excel_buffer = generate_excel_file(financial_data)
    
    output_file = "test_pivot_format.xlsx"
    with open(output_file, 'wb') as f:
        f.write(excel_buffer.getvalue())
    
    print(f"✓ Excel file created: {output_file}")
    
    # Read back and show structure
    df = pd.read_excel(output_file)
    print(f"\n✅ Excel Pivot Table Structure:")
    print(f"  Dimensions: {len(df)} rows × {len(df.columns)} columns")
    print(f"  Columns: {list(df.columns)}")
    print(f"\n📊 Sample output (first 10 rows):")
    print(df.head(10).to_string())
    
    file_size = os.path.getsize(output_file)
    print(f"\n✓ File saved successfully ({file_size/1024:.1f} KB)")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
