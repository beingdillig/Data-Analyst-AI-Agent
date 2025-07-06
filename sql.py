import pandas as pd
from sqlalchemy import create_engine
import os

# Step 1: Specify your file
data_file = "data.xlsx"  # Change to your file name

# Step 2: Create SQLite engine
engine = create_engine('sqlite:///sample.db')

# Step 3: Get file extension
file_ext = os.path.splitext(data_file)[-1].lower()

# Step 4: Load and upload based on file type
if file_ext == '.xlsx':
    # Read all sheets from Excel
    sheets = pd.read_excel(data_file, sheet_name=None, engine='openpyxl')
    for sheet_name, df in sheets.items():
        df.to_sql(sheet_name, con=engine, if_exists='replace', index=False)
        print(f"✅ Uploaded sheet '{sheet_name}' to SQLite table '{sheet_name}'")

elif file_ext == '.csv':
    # Read single CSV file
    df = pd.read_csv(data_file)
    table_name = os.path.splitext(os.path.basename(data_file))[0]  # file name without extension
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f"✅ Uploaded CSV to SQLite table '{table_name}'")

else:
    print("❌ Unsupported file format. Please provide a .csv or .xlsx file.")

