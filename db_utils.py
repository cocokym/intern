import mysql.connector
import pandas as pd
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self):
        # Get MySQL host from environment variable or use default
        self.config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'user': os.getenv('MYSQL_USER', 'remote_user'),
            'password': os.getenv('MYSQL_PASSWORD', 'password'),
            'database': 'patients_db'
        }

    def get_connection(self):
        try:
            return mysql.connector.connect(**self.config)
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                raise Exception("Invalid username or password")
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                raise Exception("Database does not exist")
            else:
                raise Exception(f"Connection failed: {err}")

    def get_patient_by_lab_number(self, lab_number):
        """Get patient by either lab number or IM lab number"""
        query = """
            SELECT * FROM patients 
            WHERE lab_number = %s OR im_lab_number = %s
        """
        try:
            conn = self.get_connection()
            df = pd.read_sql_query(query, conn, params=(lab_number, lab_number))
            return df
        finally:
            if 'conn' in locals():
                conn.close()

    def add_patient(self, patient_data):
        """Add new patient to database"""
        query = """
            INSERT INTO patients (
                report_date, lab_number, im_lab_number, name, hkid,
                dob, sex, age, ethnicity, specimen_collected,
                specimen_arrived, case_history, type_of_test, type_of_findings
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (
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
                patient_data['specimen_arrived'],
                patient_data['Case'],
                patient_data['type_of_test'],
                patient_data['type_of_findings']
            ))
            conn.commit()
            return True, "Patient added successfully"
        except Exception as e:
            return False, str(e)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_all_patients(self):
        """Get all patients"""
        try:
            conn = self.get_connection()
            df = pd.read_sql_query("SELECT * FROM patients", conn)
            return df
        finally:
            if 'conn' in locals():
                conn.close()