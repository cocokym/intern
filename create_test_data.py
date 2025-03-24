import pandas as pd
import sqlite3
from datetime import datetime, timedelta

# Create test data
test_data = {
    'Reported date': [
        '2024-02-05',
        '2024-02-04',
        '2024-02-03',
        '2024-02-02',
        '2024-02-01'
    ],
    'Lab. no.': [
        '24IG001731',
        '24IG001732',
        '24IG001733',
        '24IG001734',
        '24IG001735'
    ],
    'IM Lab. no.': [
        'IM123',
        'IM124',
        'IM125',
        'IM126',
        'IM127'
    ],
    'Patient name': [
        'CHAN TAI MAN',
        'WONG MEI MEI',
        'LAM SIU MING',
        'LEE WING YAN',
        'CHEUNG KA WAI'
    ],
    'HKID': [
        'Y3213210',
        'A1234567',
        'B9876543',
        'C4567890',
        'D7654321'
    ],
    'DOB': [
        '1995-01-01',
        '1988-05-15',
        '1976-12-25',
        '1992-07-30',
        '1985-03-18'
    ],
    'Sex/Age': [
        'M/29',
        'F/36',
        'M/48',
        'F/32',
        'F/39'
    ],
    'Ethnicity': [
        'Chinese',
        'Chinese',
        'Filipino',
        'Chinese',
        'Indonesian'
    ],
    'Sample collection date': [
        '2024-02-04',
        '2024-02-03',
        '2024-02-02',
        '2024-02-01',
        '2024-01-31'
    ],
    'Sample receive date': [
        '2024-02-04',
        '2024-02-03',
        '2024-02-02',
        '2024-02-01',
        '2024-01-31'
    ]
}

# Create DataFrame
df = pd.DataFrame(test_data)

# Save to Excel
df.to_excel('IM_Patient_List.xlsx', index=False)

# Save to SQLite database
def init_db():
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    
    # Create table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TEXT,
            lab_number TEXT,
            im_lab_number TEXT,
            name TEXT,
            hkid TEXT,
            dob TEXT,
            sex TEXT,
            age INTEGER,
            ethnicity TEXT,
            specimen_collected TEXT,
            specimen_arrived TEXT,
            UNIQUE(lab_number, im_lab_number)
        )
    ''')
    conn.commit()
    return conn

def add_patient_to_db(conn, row):
    c = conn.cursor()
    sex, age = row['Sex/Age'].split('/')
    
    try:
        c.execute('''
            INSERT INTO patients (
                report_date, lab_number, im_lab_number, name, hkid, 
                dob, sex, age, ethnicity, specimen_collected, specimen_arrived
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['Reported date'],
            row['Lab. no.'],
            row['IM Lab. no.'],
            row['Patient name'],
            row['HKID'],
            row['DOB'],
            sex,
            int(age),
            row['Ethnicity'],
            row['Sample collection date'],
            row['Sample receive date']
        ))
    except sqlite3.IntegrityError:
        print(f"Patient with Lab # {row['Lab. no.']} or IM Lab # {row['IM Lab. no.']} already exists")

# Initialize database and add test data
conn = init_db()
for _, row in df.iterrows():
    add_patient_to_db(conn, row)
conn.commit()
conn.close()

print("Test data has been created in both 'IM_Patient_List.xlsx' and 'patients.db'") 