import pandas as pd
import os

source_dir = '/mnt/c/Users/Asus/Desktop/Mncl'
files = [f for f in os.listdir(source_dir) if f.endswith('.xlsx')]

if files:
    target_file = os.path.join(source_dir, files[0])
    print(f"Probing file: {target_file}")
    xl = pd.ExcelFile(target_file)
    print(f"Sheets: {xl.sheet_names}")
    for sheet in xl.sheet_names:
        if sheet not in ["Hrs Summary", "Summary", "Total"]:
            df = xl.parse(sheet)
            print(f"\nSheet: {sheet}")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Dtypes:\n{df.dtypes}")
            print(f"First few rows:\n{df.head(2)}")
            break
else:
    print("No Excel files found.")
