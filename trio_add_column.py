import pandas as pd

def process_trio(input_path, output_path):
    # Read Excel file starting from second row (index=1)
    df = pd.read_excel(input_path, skiprows=1)
    
    # Define the column order before new columns
    before_columns = [
        "Chr:Pos",
        "Ref/Alt",
        "Primary Findings",
        "Incidental Findings"
    ]
    
    # New columns to add
    new_columns = [
        "IGV review (True / False call)",
        "Zygosity(new)",
        "Phenotype",
        "First review and comment",
        "Second review and comment on reportable variant",
        "Special remarks"
    ]
    
    # Create a new DataFrame
    new_df = pd.DataFrame()
    
    # Add Reportable Variant as first column
    new_df["Reportable Variant"] = ""
    
    # Add columns before the new columns
    for col in before_columns:
        if col in df.columns:
            new_df[col] = df[col]
    
    # Add new columns (empty)
    for col in new_columns:
        new_df[col] = ""
    
    # Add remaining columns
    remaining_cols = [col for col in df.columns if col not in before_columns]
    for col in remaining_cols:
        new_df[col] = df[col]
    
    # Save to Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        new_df.to_excel(writer, index=False)