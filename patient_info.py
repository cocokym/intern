from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from datetime import datetime
import re
from docx import Document
import os
from docx.shared import Pt
import sqlite3

app = Flask(__name__)

# Global variable to store the DataFrame
df = None

def load_excel_data():
    global df
    try:
        # Read the Excel file
        df = pd.read_excel('IM_Patient_List.xlsx')
        
        # Process Sex/Age column
        df[['Sex', 'Age']] = df['Sex/Age'].str.split('/', expand=True)
        
        # Clean up column names and create mapping
        df = df.rename(columns={
            'Reported date': 'report_date',
            'Lab. no.': 'lab_number',
            'IM Lab. no.': 'im_lab_number',
            'Patient name': 'name',
            'HKID': 'hkid',
            'DOB': 'dob',
            'Ethnicity': 'ethnicity',
            'Sample collection date': 'specimen_collected',
            'Sample receive date': 'specimen_arrived'
        })
        
        return True
    except Exception as e:
        print(f"Error loading Excel file: {str(e)}")
        return False

def validate_lab_number(lab_number):
    im_pattern = r'^IM\d{3}$'
    num_pattern = r'^2\d{10}$'
    return bool(re.match(im_pattern, lab_number) or re.match(num_pattern, lab_number))

def create_word_document(patient_data):
    try:
        # Create a new document without template
        output_doc = Document()
        
        # Set default font for the document
        style = output_doc.styles['Normal']
        style.font.name = 'Calibri'
        style.font.size = Pt(12)
        
        # Add report date with label and proper formatting
        p = output_doc.add_paragraph()
        p.add_run("REPORT DATE: ").bold = True
        # Convert date format from YYYY-MM-DD to DD/MM/YYYY
        date_obj = datetime.strptime(patient_data['report_date'], '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d/%m/%Y')
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
        p.add_run("-" * 117)  # Add 100 dashes as a separator line
        
        # Create filename using lab number and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"patient_info_{patient_data['lab_number']}_{timestamp}.docx"
        
        # Save the document
        output_doc.save(filename)
        return filename
    except Exception as e:
        print(f"Error creating Word document: {str(e)}")
        return None

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
    
    if not validate_lab_number(lab_number):
        return jsonify({
            'success': False,
            'message': 'Invalid lab number format. Please use IMxxx or 2xxxxxxxxxx format.'
        })

    # Search in both lab_number and im_lab_number columns
    result = df[(df['lab_number'] == lab_number) | (df['im_lab_number'] == lab_number)]

    if not result.empty:
        # Get the first matching record
        patient = result.iloc[0]
        
        # Prepare patient data
        patient_data = {
            'report_date': patient['report_date'].strftime('%Y-%m-%d') if pd.notnull(patient['report_date']) else '',
            'im_lab_number': str(patient['im_lab_number']),
            'lab_number': str(patient['lab_number']),
            'name': str(patient['name']),
            'hkid': str(patient['hkid']),
            'dob': patient['dob'].strftime('%Y-%m-%d') if pd.notnull(patient['dob']) else '',
            'sex': str(patient['Sex']),
            'age': str(patient['Age']),
            'ethnicity': str(patient['ethnicity']),
            'specimen_collected': patient['specimen_collected'].strftime('%Y-%m-%d') if pd.notnull(patient['specimen_collected']) else '',
            'specimen_arrived': patient['specimen_arrived'].strftime('%Y-%m-%d') if pd.notnull(patient['specimen_arrived']) else ''
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

def add_new_patient(patient_data):
    """Add a new patient to both Excel and database"""
    try:
        # Add to database
        conn = sqlite3.connect('patients.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO patients (
                report_date, lab_number, im_lab_number, name, hkid, 
                dob, sex, age, ethnicity, specimen_collected, specimen_arrived
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patient_data['report_date'],
            patient_data['lab_number'],
            patient_data['im_lab_number'],
            patient_data['name'],
            patient_data['hkid'],
            patient_data['dob'],
            patient_data['sex'],
            patient_data['age'],
            patient_data['ethnicity'],
            patient_data['specimen_collected'],
            patient_data['specimen_arrived']
        ))
        
        conn.commit()
        conn.close()
        
        # Add to Excel
        global df
        df.loc[len(df)] = patient_data
        df.to_excel('IM_Patient_List.xlsx', index=False)
        
        return True, "Patient added successfully"
    except Exception as e:
        return False, str(e)

# Add a new route for adding patients
@app.route('/add_patient', methods=['POST'])
def add_patient():
    try:
        patient_data = request.get_json()
        success, message = add_new_patient(patient_data)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    # Load data when starting the application
    load_excel_data()
    app.run(debug=True)
