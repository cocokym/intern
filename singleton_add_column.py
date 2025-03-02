import pandas as pd
from openpyxl import load_workbook

def process_singleton(input_path, output_path):
    # Read Excel file starting from second row (index=1)
    df = pd.read_excel(input_path, skiprows=1)
    
    # Create a new DataFrame
    new_df = pd.DataFrame()
    
    # Add Reportable Variant as first column
    new_df["Reportable Variant"] = ""
    
    # Add required columns with their data
    required_columns = ["Chr:Pos", "Ref/Alt", "Identifier"]
    for col in required_columns:
        if col in df.columns:
            new_df[col] = df[col]
    
    # Add new columns (empty)
    new_columns = [
        "IGV review (True / False call)",
        "Zygosity(new)",
        "Phenotype",
        "First review and comment",
        "Second review and comment on reportable variant",
        "Special remarks"
    ]
    for col in new_columns:
        new_df[col] = ""
    
    # Add 13 empty columns with unique internal names but empty display names
    current_cols = len(new_df.columns)
    for i in range(13):
        col_position = current_cols + i
        new_df[f'empty_{i}'] = ""  # Internal unique name
        # Rename the column to empty string for display
        new_df = new_df.rename(columns={f'empty_{i}': ''})
    
    # Add remaining columns from original DataFrame
    remaining_cols = [col for col in df.columns if col not in required_columns]
    for col in remaining_cols:
        new_df[col] = df[col]
    
    # Save to Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        new_df.to_excel(writer, index=False)

def add_columns_to_singleton(input_path, output_path):
    wb = load_workbook(input_path)
    ws = wb.active
    
    # Add 'Reportable Variant' to column A, row 2 only
    ws.insert_cols(1)