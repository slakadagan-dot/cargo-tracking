import sqlite3

# İzin verilen kargo durumları
STATUSES = ["CREATED", "SHIPPED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"]

def get_db_connection():
    # Veritabanı dosyasını oluşturur ve bağlanır
    conn = sqlite3.connect('cargo.db')
    # Verileri sözlük (dictionary) formatında almamızı sağlar
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Kargo tablosunu oluşturuyoruz[cite: 1]
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cargo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT NOT NULL,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    