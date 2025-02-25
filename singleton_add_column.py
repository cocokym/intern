from openpyxl import load_workbook
from openpyxl.worksheet.cell_range import CellRange

def add_columns_to_singleton(file_path):
    wb = load_workbook(file_path)
    ws = wb.active

    # Insert 'Reportable Variant' at column A
    ws.insert_cols(1)
    ws.cell(row=2, column=1, value='Reportable Variant')

    # Adjust all merged cells
    for merged_cell in list(ws.merged_cells.ranges):
        ws.merged_cells.remove(merged_cell)
        new_range = CellRange(min_col=merged_cell.min_col + 1, min_row=merged_cell.min_row,
                              max_col=merged_cell.max_col + 1, max_row=merged_cell.max_row)
        ws.merged_cells.add(new_range)

    # Insert new columns after 'Chr:Pos Ref/Alt Identifier' (assuming these are in columns B-D)
    new_columns = [
        'IGV review (True / False call)', 'Zyogosity', 'Phenotype',
        'First review and comment', 'Second review and comment on reportable variant',
        'Special remarks'
    ]
    for i, col in enumerate(new_columns, start=5):
        ws.insert_cols(i)
        ws.cell(row=2, column=i, value=col)

    # Add 12 empty columns after the new columns
    for i in range(12):
        ws.insert_cols(11 + i)
        ws.cell(row=2, column=11 + i, value='')

    # Save the modified workbook
    wb.save(file_path)