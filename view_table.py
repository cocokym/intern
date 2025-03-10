import mysql.connector
import pandas as pd
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)        # Don't wrap long strings
pd.set_option('display.max_rows', None)     # Show all rows

def view_patients():
    # MySQL configuration
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'patients_db'
    }

    try:
        # Connect to database
        conn = mysql.connector.connect(**config)
        
        # Query data
        query = """
        SELECT 
            lab_number,
            im_lab_number,
            name,
            hkid,
            sex,
            age,
            case_history,
            type_of_test,
            type_of_findings
        FROM patients
        ORDER BY created_at DESC
        """
        
        # Load into DataFrame
        df = pd.read_sql_query(query, conn)
        
        # Display the table
        print("\n=== Patients Database Contents ===")
        print(f"Total Records: {len(df)}")
        print("\nData Preview:")
        print(df)
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    view_patients()