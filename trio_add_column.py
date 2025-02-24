from openpyxl import load_workbook

def add_columns_to_trio(file_path):
    wb = load_workbook(file_path)
    ws = wb.active

    new_columns = [
        'Reportable Variant', 'IGV review (True / False call)', 'Zyogosity', 'Phenotype',
        'First review and comment', 'Second review and comment on reportable variant',
        'Special remarks'
    ]

    # Insert 'Reportable Variant' at column A
    ws.insert_cols(1)
    ws.cell(row=2, column=1, value='Reportable Variant')

    # Insert new columns after 'Flags' (assuming 'Flags' is in column E)
    for i, col in enumerate(new_columns[1:], start=6):
        ws.insert_cols(i)
        ws.cell(row=2, column=i, value=col)

    
    wb.save(file_path)