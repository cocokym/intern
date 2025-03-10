import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime

def initialize_database():
    # MySQL configuration
    config = {
        'host': 'localhost',
        'user': 'root',  # Your MySQL username
        'password': 'password'   # Your MySQL password
    }

    try:
        # Create database connection
        print("Connecting to MySQL...")
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Create and use database
        print("Creating database...")
        cursor.execute("DROP DATABASE IF EXISTS patients_db")
        cursor.execute("CREATE DATABASE patients_db")
        cursor.execute("USE patients_db")
        
        # Create patients table with proper columns
        print("Creating patients table...")
        cursor.execute("""
            CREATE TABLE patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                report_date TEXT,          # Changed from DATE to TEXT
                lab_number VARCHAR(255),   # Increased from VARCHAR(20)
                im_lab_number VARCHAR(255),# Increased from VARCHAR(20)
                name VARCHAR(100),
                hkid VARCHAR(20),
                dob TEXT,                  # Changed from DATE to TEXT
                sex VARCHAR(1),
                age VARCHAR(10),
                ethnicity VARCHAR(50),
                specimen_collected TEXT,    # Changed from DATE to TEXT
                specimen_arrived TEXT,      # Changed from DATE to TEXT
                case_history TEXT,
                type_of_test VARCHAR(50),
                type_of_findings VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # Read Excel file
        print("\nReading Excel file...")
        df = pd.read_excel('IM patient list_20250303_template.xlsx', header=1)
        
        # Store original data for comparison
        original_lab_numbers = set(df['Lab. no.'].dropna())
        original_im_numbers = set(df['IM Lab. no.'].dropna())
        
        # Clean data
        df = df.replace({np.nan: None})
        
        # Add validation counters
        total_rows = len(df)
        empty_rows = 0
        skipped_rows = []
        processed_lab_numbers = set()
        processed_im_numbers = set()
        
        print("\nStarting data validation...")
        print(f"Total rows in Excel: {total_rows}")
        
        # Process data and insert
        success_count = 0
        error_count = 0
        error_details = []
        
        for index, row in df.iterrows():
            try:
                # Only skip if ALL fields are empty
                all_empty = all(pd.isna(value) for value in row.values)
                if all_empty:
                    empty_rows += 1
                    continue

                lab_no = row.get('Lab. no.', '')
                im_lab_no = row.get('IM Lab. no.', '')
                
                # Track processed numbers
                if pd.notnull(lab_no):
                    processed_lab_numbers.add(str(lab_no).strip())
                if pd.notnull(im_lab_no):
                    processed_im_numbers.add(str(im_lab_no).strip())
                
                # Enhanced error tracking
                if pd.isna(row['Lab. no.']) and pd.isna(row['IM Lab. no.']):
                    error_details.append({
                        'row': index + 2,
                        'reason': 'Both Lab No. and IM Lab No. are empty',
                        'patient': row.get('Patient name', 'Unknown')
                    })
                    error_count += 1
                    continue

                # Add debug printing for each row
                print(f"\nProcessing row {index + 2}:")
                print(f"Lab No: {row.get('Lab. no.', '')}")
                print(f"IM Lab No: {row.get('IM Lab. no.', '')}")
                print(f"Patient Name: {row.get('Patient name', '')}")

                insert_query = """
                    INSERT INTO patients (
                        report_date, lab_number, im_lab_number, name,
                        hkid, dob, sex, age, ethnicity,
                        specimen_collected, specimen_arrived, case_history,
                        type_of_test, type_of_findings
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Process Sex/Age
                sex_age = str(row.get('Sex/Age', ''))
                sex, age = sex_age.split('/') if '/' in sex_age else ('', '')
                
                values = (
                    str(row.get('Singe gene Reported date', '')).strip(),  # Store as text
                    str(row.get('Lab. no.', '')).strip(),
                    str(row.get('IM Lab. no.', '')).strip(),
                    str(row.get('Patient name', '')).strip(),
                    str(row.get('HKID', '')).strip(),
                    str(row.get('DOB', '')).strip(),                       # Store as text
                    sex.strip(),
                    age.strip(),
                    str(row.get('Ethnicity', '')).strip(),
                    str(row.get('Sample collection date', '')).strip(),    # Store as text
                    str(row.get('Sample receive date', '')).strip(),       # Store as text
                    str(row.get('Case', '')).strip(),
                    str(row.get('Type of test', '')).strip(),
                    str(row.get('Type of findings', '')).strip()
                )
                
                cursor.execute(insert_query, values)
                success_count += 1
                
                if success_count % 100 == 0:  # Progress indicator
                    print(f"Processed {success_count} records...")
                
            except Exception as e:
                error_details.append({
                    'row': index + 2,
                    'reason': str(e),
                    'patient': row.get('Patient name', 'Unknown'),
                    'lab_no': lab_no,
                    'im_lab_no': im_lab_no
                })
                error_count += 1
                continue

        # After processing, find missing records
        missing_lab_numbers = original_lab_numbers - processed_lab_numbers
        missing_im_numbers = original_im_numbers - processed_im_numbers

        # Commit changes
        conn.commit()
        
        # Enhanced summary with missing records details
        print("\n=== Import Summary ===")
        print(f"Total rows in Excel: {total_rows}")
        print(f"Empty rows skipped: {empty_rows}")
        print(f"Successfully imported: {success_count}")
        print(f"Failed to import: {error_count}")
        
        if missing_lab_numbers or missing_im_numbers:
            print("\n=== Missing Records ===")
            print("Lab numbers not imported:")
            for lab in missing_lab_numbers:
                missing_row = df[df['Lab. no.'] == lab].iloc[0]
                print(f"Row {df[df['Lab. no.'] == lab].index[0] + 2}:")
                print(f"  Lab No: {lab}")
                print(f"  Patient Name: {missing_row.get('Patient name', '')}")
                print(f"  Case: {missing_row.get('Case', '')}")
                
            print("\nIM Lab numbers not imported:")
            for im_lab in missing_im_numbers:
                missing_row = df[df['IM Lab. no.'] == im_lab].iloc[0]
                print(f"Row {df[df['IM Lab. no.'] == im_lab].index[0] + 2}:")
                print(f"  IM Lab No: {im_lab}")
                print(f"  Patient Name: {missing_row.get('Patient name', '')}")
                print(f"  Case: {missing_row.get('Case', '')}")

        # Enhanced error reporting
        if error_details:
            print("\n=== Import Errors Details ===")
            print(f"Total errors: {error_count}")
            for error in error_details:
                print(f"\nRow {error['row']}:")
                print(f"  Patient: {error['patient']}")
                if 'lab_no' in error:
                    print(f"  Lab No: {error['lab_no']}")
                if 'im_lab_no' in error:
                    print(f"  IM Lab No: {error['im_lab_no']}")
                print(f"  Reason: {error['reason']}")

        # Verify data with detailed count
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT lab_number) as unique_lab,
                COUNT(DISTINCT im_lab_number) as unique_im
            FROM patients
        """)
        counts = cursor.fetchone()
        print(f"\nDatabase Statistics:")
        print(f"Total records: {counts[0]}")
        print(f"Unique lab numbers: {counts[1]}")
        print(f"Unique IM lab numbers: {counts[2]}")
        
        return True
        
    except Exception as e:
        print(f"\nDatabase initialization error: {str(e)}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print("Starting database initialization...")
    initialize_database()