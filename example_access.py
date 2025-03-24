from db_utils import DatabaseManager
import pandas as pd

def example_data_access():
    # Initialize database manager
    db = DatabaseManager()
    
    try:
        # Get all patients
        all_patients = db.get_all_patients()
        print(f"Total patients: {len(all_patients)}")
        
        # Get specific patient
        lab_number = "IM123"
        patient = db.get_patient_by_lab_number(lab_number)
        if not patient.empty:
            print(f"Found patient: {patient.iloc[0]['name']}")
            
    except Exception as e:
        print(f"Error accessing database: {str(e)}")

if __name__ == '__main__':
    example_data_access()