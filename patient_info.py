from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from datetime import datetime
import re
from docx import Document
import os
from docx.shared import Pt
import sqlite3
from db_utils import DatabaseManager

app = Flask(__name__)

# Global variable to store the DataFrame
df = None

# Update the database configuration
db = DatabaseManager()

# Add error handling for database connection
def load_patient_data():
    """Load patient data from database"""
    try:
        return db.get_all_patients()
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None

def load_excel_data():
    global df
    try:
        # Read the Excel file
        df = pd.read_excel('IM patient list_20250303_template.xlsx', header=1)
        
        # Print original columns for debugging
        print("Original columns before mapping:", df.columns.tolist())
        
        # First, handle unnamed columns if they exist
        unnamed_mapping = {}
        for col in df.columns:
            if 'Unnamed' in str(col):
                col_index = int(col.split(':')[1])
                if col_index == 0:
                    unnamed_mapping[col] = 'IM Lab. no.'
                elif col_index == 1:
                    unnamed_mapping[col] = 'Lab. no.'
                elif col_index == 2:
                    unnamed_mapping[col] = 'Patient name'
                # ... add more mappings as needed
        
        if unnamed_mapping:
            df = df.rename(columns=unnamed_mapping)
        
        # Now map to our standardized names
        column_mapping = {
            'Singe gene Reported date': 'report_date',
            'Lab. no.': 'lab_number',
            'IM Lab. no.': 'im_lab_number',
            'Patient name': 'name',
            'HKID': 'hkid',
            'DOB': 'dob',
            'Ethnicity': 'ethnicity',
            'Sample collection date': 'specimen_collected',
            'Sample receive date': 'specimen_arrived',
            'Sex/Age': 'Sex/Age',
            'Case': 'case_history',  # Map 'Case' to 'case_history'
            'Type of test': 'type_of_test',
            'Type of findings': 'type_of_findings'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Process Sex/Age column
        if 'Sex/Age' in df.columns:
            # Split Sex/Age and create new columns
            df[['sex', 'age']] = df['Sex/Age'].str.split('/', expand=True)
            # Clean the new columns
            df['sex'] = df['sex'].astype(str).str.strip()
            df['age'] = df['age'].astype(str).str.strip()
        
        # Convert relevant columns to string and clean them
        string_columns = ['im_lab_number', 'lab_number', 'name', 'hkid', 'ethnicity', 'clinical_history', 'type_of_test', 'type_of_findings']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('nan', '')
        
        # Convert date columns to datetime
        date_columns = ['report_date', 'dob', 'specimen_collected', 'specimen_arrived']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Print debug information
        print("\nFinal columns:", df.columns.tolist())
        print("\nFirst row:")
        print(df.iloc[0])
        
        return True
    except Exception as e:
        print(f"Error in load_excel_data: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def validate_lab_number(lab_number):
    im_pattern = r'^IM\d{3}$'
    num_pattern = r'^2\d{10}$'
    return bool(re.match(im_pattern, lab_number) or re.match(num_pattern))

def create_word_document(patient_data):
    try:
        output_doc = Document()
        
        style = output_doc.styles['Normal']
        style.font.name = 'Calibri'
        style.font.size = Pt(12)
        
        # Add report date with label and proper formatting
        p = output_doc.add_paragraph()
        p.add_run("REPORT DATE: ").bold = True
        # Handle date formatting safely
        try:
            if patient_data['report_date']:
                date_obj = datetime.strptime(patient_data['report_date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d/%m/%Y')
            else:
                formatted_date = ''
        except:
            formatted_date = patient_data['report_date']
        p.add_run(formatted_date).bold = True
        
        # Add patient information with formatting
        info = [
            ('Lab. #', f"{patient_data['im_lab_number']}/{patient_data['lab_number']}"),
            ('Name', patient_data['name']),
            ('HKID', patient_data['hkid']),
            ('Date of Birth', patient_data['dob']),
            ('Sex', patient_data['sex']),
            ('Age', patient_data['age']),
            ('Ethnicity', patient_data['ethnicity']),
            ('Specimen Collected', patient_data['specimen_collected']),
            ('Specimen Arrived', patient_data['specimen_arrived'])
        ]
        
        for label, value in info:
            p = output_doc.add_paragraph()
            p.add_run(f"{label}: ").bold = True
            # Format dates if the value is a date
            if label in ['Date of Birth', 'Specimen Collected', 'Specimen Arrived'] and value:
                try:
                    date_obj = datetime.strptime(value, '%Y-%m-%d')
                    value = date_obj.strftime('%d/%m/%Y')
                except ValueError:
                    pass
            p.add_run(str(value))
        
        # Add line separator at the end
        p = output_doc.add_paragraph()
        p.add_run("-" * 117)
        
        # Add new sections after separator with titles on separate lines
        sections = [
            ('SPECIMEN', 'EDTA blood'),
            ('CLINICAL HISTORY', patient_data['clinical_history']),  # Use clinical_history key
            ('TYPE OF TESTING REQUESTED', patient_data.get('type_of_test', '')),
            ('TEST DESCRIPTION', get_test_description(patient_data.get('test_type', ''))),
            ('SUMMARY OF RESULT(S)', get_summary_result(patient_data.get('type_of_findings', '')))
        ]
        
        for label, value in sections:
            # Add title paragraph
            p = output_doc.add_paragraph()
            p.add_run(f"{label}:").bold = True
            
            # Add value on next line
            p = output_doc.add_paragraph()
            p.add_run(str(value))
        
        # Create filename using lab number and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"patient_info_{patient_data['lab_number']}_{timestamp}.docx"
        
        # Save the document
        output_doc.save(filename)
        return filename
    except Exception as e:
        print(f"Error creating Word document: {str(e)}")
        return None

def get_test_description(test_type):
    base_desc = "In-house Immunological Disorders SuperPanel gene panel from WES was tested by next generation sequencing, and 516 genes were included in the panel test."
    if test_type.lower() == 'trio':
        return f"{base_desc} Trio analysis has been performed."
    return base_desc

def get_summary_result(finding_type):
    if finding_type == 'A':
        return "No disease-causing variant detected to fully account for the patient's phenotype. However, details on some additional findings have been included for reference."
    elif finding_type in ['I', 'N']:
        return "No disease-causing variant detected to fully account for the patient's phenotype."
    elif finding_type == 'C':
        return "/"
    return ""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    global df
    if df is None:
        if not load_excel_data():
            return jsonify({
                'success': False,
                'message': 'Error loading patient database.'
            })

    lab_number = request.form.get('lab_number')
    test_type = request.form.get('test_type')
    
    if not validate_lab_number(lab_number):
        return jsonify({
            'success': False,
            'message': 'Invalid lab number format. Please use IMxxx or 2xxxxxxxxxx format.'
        })

    result = df[(df['lab_number'] == lab_number) | (df['im_lab_number'] == lab_number)]

    if not result.empty:
        patient = result.iloc[0]
        
        # Handle dates safely
        def format_date(date_value):
            if pd.isna(date_value):
                return ''
            try:
                if isinstance(date_value, str):
                    # Try to parse the string date
                    try:
                        date_obj = pd.to_datetime(date_value).date()
                        return date_obj.strftime('%Y-%m-%d')
                    except:
                        return date_value
                return date_value.date().strftime('%Y-%m-%d')
            except:
                return str(date_value)

        # Prepare patient data with safe date handling
        patient_data = {
            'report_date': format_date(patient['report_date']),
            'im_lab_number': str(patient['im_lab_number']),
            'lab_number': str(patient['lab_number']),
            'name': str(patient['name']),
            'hkid': str(patient['hkid']),
            'dob': format_date(patient['dob']),
            'sex': str(patient['sex']),
            'age': str(patient['age']),
            'ethnicity': str(patient['ethnicity']),
            'specimen_collected': format_date(patient['specimen_collected']),
            'specimen_arrived': format_date(patient['specimen_arrived']),
            'clinical_history': str(patient['case_history']),  # Use mapped column name
            'type_of_test': str(patient['type_of_test']),
            'test_type': request.form.get('test_type'),
            'type_of_findings': str(patient['type_of_findings'])
        }
        
        # Create Word document
        doc_filename = create_word_document(patient_data)
        
        if doc_filename:
            return jsonify({
                'success': True,
                'data': patient_data,
                'document': doc_filename
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error creating Word document.'
            })
    else:
        return jsonify({
            'success': False,
            'message': 'No patient found with this lab number.'
        })

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return str(e)

# Update add_new_patient function
def add_new_patient(patient_data):
    """Add new patient using database manager"""
    return db.add_patient(patient_data)

# Add a new route for adding patients
@app.route('/add_patient', methods=['POST'])
def add_patient():
    try:
        patient_data = request.get_json()
        
        # Validate required fields
        required_fields = ['lab_number', 'im_lab_number', 'name']
        for field in required_fields:
            if not patient_data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                })
        
        # Add timestamp
        patient_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save to database
        success = db.add_patient(patient_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Patient added successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to add patient'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Add new route for getting all patients
@app.route('/get_patients')
def get_patients():
    try:
        # Get fresh data from database each time
        patients = db.get_all_patients()
        return jsonify({
            'success': True,
            'data': patients.to_dict('records')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

if __name__ == '__main__':
    # Load data from database when starting
    df = load_patient_data()
    if df is None:
        print("Failed to load from database, trying Excel file...")
        if not load_excel_data():
            print("Failed to load data from both database and Excel!")
    else:
        print("Successfully loaded data from database")
    
    app.run(debug=True)
