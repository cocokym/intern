from openpyxl import load_workbook

def add_columns_to_singleton(file_path):
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

    # Insert new columns after 'Variant Info' (assuming 'Variant Info' is in columns B-D)
    for i, col in enumerate(new_columns[1:], start=5):
        ws.insert_cols(i)
        ws.cell(row=2, column=i, value=col)

    # Add 12 empty columns after 'Special remarks'
    for i in range(12):
        ws.insert_cols(11 + i)
        ws.cell(row=2, column=11 + i, value='')

    # Ensure all titles in row 1 are included
    titles = [
        'Variant Info', 'IM662', 'RefSeq Genes 110, NCBI', 'Transcript Interactions RefSeq Genes 110, NCBI',
        'gnomAD Genomes Variant Frequencies 3.1.2 v2, BROAD', 'ClinVar 2024-06-06, NCBI', 'OMIM Phenotypes 2023-06-01, GHI',
        'OMIM Genes 2023-06-01, GHI', 'REVEL Functional Predictions 2016-06-03, GHI', 'CADD Scores 1.6',
        'dbscSNV Splice Altering Predictions 1.1, GHI', 'Genomenon Mastermind 2023-07-02, GHI', 'var_20240715_IMM_v1',
        'Match ACMG SF v3.2', 'Match Mendeliome', 'Match IMM_SuperPanel_554G_v2.0'
    ]

    # Set titles in row 1
    for i, title in enumerate(titles, start=2):
        cell = ws.cell(row=1, column=i)
        cell.value = title

    # Save the modified workbook
    wb.save(file_path)

# Example usage
add_columns_to_singleton('singleton_row1_template.xlsx')