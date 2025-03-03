from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
import pandas as pd
from singleton_add_column import process_singleton
from trio_add_column import process_trio

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def is_trio(df):
    """Check if file has both Mother and Father columns"""
    return any("Mother" in col for col in df.columns) and any("Father" in col for col in df.columns)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file uploaded')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        flash('Invalid file type. Please upload an Excel file.')
        return redirect(url_for('index'))
    
    try:
        # Save uploaded file
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"processed_{file.filename}")
        file.save(input_path)
        
        # Read file to determine type
        df = pd.read_excel(input_path)
        
        # Process based on file type
        if is_trio(df):
            process_trio(input_path, output_path)
        else:
            process_singleton(input_path, output_path)
        
        # Flash success message with file location
        flash(f'File processed successfully! Saved as: processed_{file.filename}')
        
        return send_file(output_path, as_attachment=True)
    
    except Exception as e:
        flash(f'Error processing file: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5001)  # Changed port to 5001