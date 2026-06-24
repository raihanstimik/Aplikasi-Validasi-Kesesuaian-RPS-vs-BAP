import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'pbo_rps_bap')
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print("✅ Koneksi MySQL berhasil")
            return True
        except Error as e:
            print(f"❌ Error koneksi: {e}")
            return False

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()

    def execute_query(self, query, params=None):
        if not self.connect():
            return None
        try:
            self.cursor.execute(query, params or ())
            if query.strip().upper().startswith("SELECT"):
                return self.cursor.fetchall()
            self.conn.commit()
            return self.cursor.rowcount
        except Error as e:
            print(f"❌ Query Error: {e}")
            return None
        finally:
            self.close()