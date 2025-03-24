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

    def update_findings(self, lab_number, findings):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Try updating by lab_number first
                cursor.execute("""
                    UPDATE patients 
                    SET type_of_findings = %s 
                    WHERE lab_number = %s OR im_lab_number = %s
                """, (findings, lab_number, lab_number))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating findings: {str(e)}")
            return False

    def search_patients(self, search_term):
        """Search patients by lab number or IM lab number"""
        try:
            conn = self.get_connection()
            query = """
            SELECT * FROM patients 
            WHERE lab_number LIKE %s 
            OR im_lab_number LIKE %s
            OR name LIKE %s
            """
            search_pattern = f"%{search_term}%"
            df = pd.read_sql_query(query, conn, params=[search_pattern, search_pattern, search_pattern])
            return df
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_patient(self, lab_number):
        """Delete patient by lab number"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = "DELETE FROM patients WHERE lab_number = %s"
            cursor.execute(query, (lab_number,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting patient: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def get_patient(self, lab_number):
        """Get single patient by lab number"""
        try:
            conn = self.get_connection()
            query = "SELECT * FROM patients WHERE lab_number = %s"
            df = pd.read_sql_query(query, conn, params=[lab_number])
            return df.to_dict('records')[0] if not df.empty else None
        finally:
            if 'conn' in locals():
                conn.close()