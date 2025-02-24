from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from singleton_add_column import add_columns_to_singleton
from trio_add_column import add_columns_to_trio
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uploads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db = SQLAlchemy(app)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    processed = db.Column(db.Boolean, default=False)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        file_type = request.form['file_type']
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], file_type)
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], file_type)

        # Create directories if they do not exist
        os.makedirs(upload_path, exist_ok=True)
        os.makedirs(processed_path, exist_ok=True)

        file.save(os.path.join(upload_path, filename))

        if file_type == 'singleton':
            add_columns_to_singleton(os.path.join(upload_path, filename))
        else:
            add_columns_to_trio(os.path.join(upload_path, filename))

        # Append timestamp to the processed file name to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        processed_filename = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
        final_path = os.path.join(processed_path, processed_filename)

        os.rename(os.path.join(upload_path, filename), final_path)

        new_upload = Upload(filename=processed_filename, file_type=file_type, processed=True)
        db.session.add(new_upload)
        db.session.commit()

        flash(f'File processed and saved at: {final_path}')
        return redirect(url_for('upload_form'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)