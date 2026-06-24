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
            # Pastikan dictionary=True agar hasil query berupa format Key-Value (Dictionary)
            self.cursor = self.conn.cursor(dictionary=True)
            return True
        except Error as e:
            print(f"❌ Error koneksi: {e}")
            return False

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()

    def execute_query(self, query, params=None):
        """Fungsi untuk INSERT, UPDATE, DELETE"""
        if not self.conn or not self.conn.is_connected():
            self.connect()
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            return self.cursor.rowcount
        except Error as e:
            print(f"⚠️ Query Error: {e}")
            return 0

    # ── tambahkan FUNGSI INI DI DALAM CLASS DATABASEMANAGER ──────────────────
    def fetch_all(self, query, params=None):
        """Fungsi pintar untuk mengambil semua baris data (SELECT)"""
        if not self.conn or not self.conn.is_connected():
            self.connect()
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall() # Mengambil semua hasil data SELECT
        except Error as e:
            print(f"⚠️ Fetch Error: {e}")
            return [] # Kembalikan list kosong jika query gagal agar tidak membuat aplikasi crash