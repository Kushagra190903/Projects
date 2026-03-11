import pandas as pd
import os

output_path = '/mnt/c/Users/Asus/Desktop/Mncl/MNCL_Master_Summary.xlsx'
if os.path.exists(output_path):
    df = pd.read_excel(output_path)
    print(f"Summary File: {output_path}")
    print(f"Total Rows: {len(df)}")
    print("\nFirst 10 rows of summary:")
    print(df.head(10))
    
    # Check if 'Total Hours (HHH:MM)' column exists and has values
    if 'Total Hours (HHH:MM)' in df.columns:
        print("\nColumn 'Total Hours (HHH:MM)' is present.")
    else:
        print("\nError: Column 'Total Hours (HHH:MM)' is missing!")
else:
    print(f"Error: Output file {output_path} not found.")
