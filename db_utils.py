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
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM patients")
                results = cursor.fetchall()
                return pd.DataFrame(results) if results else pd.DataFrame()
        except Exception as e:
            print(f"Error getting patients: {e}")
            return pd.DataFrame()

    def update_findings(self, lab_number, findings):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
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

    def update_findings_summary(self, lab_number, findings_type, summary):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE patients 
                    SET type_of_findings = %s,
                        findings_summary = %s 
                    WHERE lab_number = %s OR im_lab_number = %s
                """, (findings_type, summary, lab_number, lab_number))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating findings summary: {str(e)}")
            return False

    def update_findings_and_summary(self, lab_number, findings_type, summary=None):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if summary:
                    cursor.execute("""
                        UPDATE patients 
                        SET type_of_findings = %s,
                            findings_summary = %s 
                        WHERE lab_number = %s OR im_lab_number = %s
                    """, (findings_type, summary, lab_number, lab_number))
                else:
                    cursor.execute("""
                        UPDATE patients 
                        SET type_of_findings = %s
                        WHERE lab_number = %s OR im_lab_number = %s
                    """, (findings_type, lab_number, lab_number))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating findings and summary: {str(e)}")
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

    def get_findings_summary(self, lab_number):
        """Get findings summary for a specific lab number"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT findings_summary 
                    FROM patients 
                    WHERE lab_number = %s OR im_lab_number = %s
                """, (lab_number, lab_number))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error getting findings summary: {str(e)}")
            return None

    def save_uploaded_file(self, file_type, file_name, lab_number):
        """
        Save uploaded file information to the database.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    INSERT INTO uploaded_files (file_type, file_name, lab_number, upload_date)
                    VALUES (%s, %s, %s, NOW())
                """
                cursor.execute(query, (file_type, file_name, lab_number))
                conn.commit()
                print(f"Debug: File information saved to database: {file_name}, {lab_number}")  # Debug print
                return True
        except Exception as e:
            print(f"Error saving uploaded file: {str(e)}")  # Debug print
            return False

    def get_uploaded_file_path(self, lab_number):
        """
        Fetch the file path of the uploaded singleton or trio file for a specific patient.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT file_name
                    FROM uploaded_files
                    WHERE lab_number = %s
                    LIMIT 1
                """
                cursor.execute(query, (lab_number,))
                result = cursor.fetchone()
                print(f"Debug: Fetched file for lab number {lab_number}: {result}")  # Debug print
                if result:
                    return result[0]  # Return the file name if it exists
                return None
        except Exception as e:
            print(f"Error fetching uploaded file path for lab number {lab_number}: {str(e)}")
            return None