import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

def set_cell_font(cell, font_name='Calibri', font_size=12, is_bold=False):
    text = cell.text  # Store the existing text
    paragraph = cell.paragraphs[0]
    paragraph.clear()  # Clear existing formatting
    
    # Add the text back with new formatting
    run = paragraph.add_run(text)
    font = run.font
    font.name = font_name
    font.size = Pt(font_size)
    font.bold = is_bold

def create_gene_table(doc, row_data):
    # Create table with 4 rows and 7 columns for the main format
    table = doc.add_table(rows=4, cols=7)
    table.style = 'Table Grid'
    table.allow_autofit = False  # Disable autofit
    
    # Set column widths using cell widths
    widths = [2.11, 5.64, 1.75, 2.25, 3.0, 2.0, 2.25]  # in cm
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            cell.width = Cm(widths[idx])
    
    # Set overall table preferred width
    table.width = Cm(sum(widths))
    
    # Set row heights
    table.rows[0].height = Cm(1.25)  # First header row
    table.rows[1].height = Cm(1.25)  # First data row
    table.rows[2].height = Cm(0.7)   # Second header row
    table.rows[3].height = Cm(0.7)   # Second data row
    
    # First row headers
    headers_row1 = ['Gene name/OMIM', 'Transcript/Variant in HGVS Nomenclature', 'Exon Location', 
                   'Genotype/Zygosity', 'Inheritance', 'Parent origin', 'Classification']
    
    # Second row headers (shifted right by one cell)
    headers_row2 = ['', 'Position', 'REF/ALT', 'Assembly', 'SNP Identifier', 'Phenotype', '']
    
    # Merge cells for Phenotype (row 3, columns 5 and 6)
    cell_phenotype = table.cell(2, 5)
    cell_empty = table.cell(2, 6)
    cell_phenotype.merge(cell_empty)
    
    # Fill first row headers with formatting
    for i, header in enumerate(headers_row1):
        cell = table.cell(0, i)
        paragraph = cell.paragraphs[0]
        run = paragraph.add_run(header)
        run.font.name = 'Calibri'
        run.font.size = Pt(12)
        run.font.bold = True
        
    # Fill first row data with formatting
    row = table.rows[1]
    data = [
        f"{row_data['Gene Names']}*{row_data['Amish Female Allele Count (AC_AMI_XX)']}",
        f"{row_data['HGVS c. (Clinically Relevant)']}/{row_data['HGVS p. (Clinically Relevant)']}",
        str(row_data['Exon Number (Clinically Relevant)']),
        str(row_data['Zygosity']),
        str(row_data['African Female Allele Count (AC_AFR_XX)']),
        "",  # Parent origin empty
        str(row_data['Second review and comment on reportable variant '])
    ]
    
    for i, value in enumerate(data):
        cell = row.cells[i]
        paragraph = cell.paragraphs[0]
        run = paragraph.add_run(value)
        run.font.name = 'Calibri'
        run.font.size = Pt(12)
        # Make Gene name/OMIM content bold
        run.font.bold = (i == 0)  # Bold only for first column
    
    # Fill second row headers with formatting
    for i, header in enumerate(headers_row2[:-1]):  # Exclude the last empty header
        cell = table.cell(2, i)
        paragraph = cell.paragraphs[0]
        run = paragraph.add_run(header)
        run.font.name = 'Calibri'
        run.font.size = Pt(12)
        run.font.bold = True
        
    # Merge cells for Phenotype data (row 4, columns 5 and 6)
    cell_phenotype_data = table.cell(3, 5)
    cell_empty_data = table.cell(3, 6)
    cell_phenotype_data.merge(cell_empty_data)
    
    # Fill second row data with formatting
    row = table.rows[3]
    data = [
        "",  # First cell empty
        str(row_data['Chr:Pos']),
        str(row_data['Ref/Alt']),
        "GRCh38",
        "",  # SNP Identifier empty
        str(row_data['Title']),  # Phenotype in merged cell
    ]
    
    for i, value in enumerate(data):
        cell = row.cells[i] if i < 5 else cell_phenotype_data
        paragraph = cell.paragraphs[0]
        run = paragraph.add_run(value)
        run.font.name = 'Calibri'
        run.font.size = Pt(12)
        run.font.bold = False
    
    # Add spacing after table
    doc.add_paragraph()

def main():
    # Read the Excel file with full path
    excel_path = "/Users/admin/Desktop/code/table/patient_gene.xlsx"
    print(f"Reading Excel file from: {excel_path}")
    df = pd.read_excel(excel_path)
    print(f"Found {len(df)} rows in Excel file")
    
    # Create new document
    doc = Document()
    
    # Create a table for each row in the Excel file
    for index, row in df.iterrows():
        print(f"Creating table for row {index + 1}")
        create_gene_table(doc, row)
    
    # Save the document
    output_path = 'table_results.docx'
    doc.save(output_path)
    print(f"Tables saved to: {output_path}")

if __name__ == "__main__":
    main() 