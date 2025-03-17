import mysql.connector
import pandas as pd
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self):
        # Get MySQL host from environment variable or use default
        self.config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'user': os.getenv('MYSQL_USER', 'root'),
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
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Prepare SQL query
            fields = ', '.join(patient_data.keys())
            placeholders = ', '.join(['%s'] * len(patient_data))
            query = f"INSERT INTO patients ({fields}) VALUES ({placeholders})"
            
            # Execute query
            cursor.execute(query, list(patient_data.values()))
            conn.commit()
            
            return True
        except Exception as e:
            print(f"Error adding patient: {e}")
            return False
        finally:
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