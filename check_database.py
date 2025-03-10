import sqlite3
import pandas as pd

def check_database():
    try:
        # Connect to database
        conn = sqlite3.connect('patients.db')
        
        # Get total number of records
        count = pd.read_sql_query("SELECT COUNT(*) as count FROM patients", conn).iloc[0]['count']
        print(f"\nTotal records in database: {count}")
        
        # Get sample of records
        print("\nFirst 5 records:")
        df = pd.read_sql_query("""
            SELECT report_date, lab_number, im_lab_number, name, type_of_test 
            FROM patients LIMIT 5
        """, conn)
        print(df)
        
        # Get column names
        print("\nDatabase columns:")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(patients)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
            
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {str(e)}")

def check_report_dates():
    try:
        conn = sqlite3.connect('patients.db')
        
        # First, let's see all columns and a sample of raw data
        print("\nRaw data sample:")
        raw_query = """
        SELECT *
        FROM patients
        LIMIT 2
        """
        raw_df = pd.read_sql_query(raw_query, conn)
        print("\nColumns in database:", raw_df.columns.tolist())
        print("\nSample data:")
        print(raw_df)
        
        # Now check the report_date column specifically
        print("\nReport date values:")
        date_query = """
        SELECT report_date, COUNT(*) as count
        FROM patients
        GROUP BY report_date
        """
        date_df = pd.read_sql_query(date_query, conn)
        print(date_df)
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

def check_excel_source():
    try:
        print("\nChecking Excel source file:")
        df = pd.read_excel('IM patient list_20250303_template.xlsx', header=1)
        
        print("\nExcel columns:", df.columns.tolist())
        print("\nSinge gene Reported date column sample:")
        if 'Singe gene Reported date' in df.columns:
            print(df['Singe gene Reported date'].head())
        else:
            print("Column 'Singe gene Reported date' not found!")
            print("Available columns that might contain dates:")
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            print(date_cols)
            
    except Exception as e:
        print(f"Error checking Excel file: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    check_database()
    check_report_dates()
    check_excel_source()