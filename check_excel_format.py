import pandas as pd

# Check Dabur Excel
print("Dabur Excel File Analysis:")
print("="*60)
df_dabur = pd.read_excel('output_Dabur.xlsx')
print(f"Shape: {df_dabur.shape[0]} rows × {df_dabur.shape[1]} columns")
print(f"Columns: {list(df_dabur.columns)}")
print(f"\nFirst 5 rows:")
print(df_dabur.head())

print("\n\nTata Motors Excel File Analysis:")
print("="*60)
df_tata = pd.read_excel('output_Tata_Motors.xlsx')
print(f"Shape: {df_tata.shape[0]} rows × {df_tata.shape[1]} columns")
print(f"Columns: {list(df_tata.columns)}")
print(f"\nFirst 5 rows:")
print(df_tata.head())

# Check reference
print("\n\nComparison with Reference Format:")
print("="*60)
df_ref = pd.read_excel('../Financial\ Statements\ Examples.xlsx')
print(f"Reference file:")
print(f"Shape: {df_ref.shape[0]} rows × {df_ref.shape[1]} columns")
print(f"Columns: {list(df_ref.columns)}")
print(f"First 5 rows:")
print(df_ref.head())
