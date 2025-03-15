from db_utils import DatabaseManager

def test_connection():
    db = DatabaseManager()
    try:
        conn = db.get_connection()
        print("Successfully connected to MySQL!")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()

