# database.py - MySQL Database Connection
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'AppleBanana2006@123',
    'database': 'personal_finance',
    'port': 3306
}

def get_db_connection():
    """Returns a MySQL connection or None if failed."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"[DBMS Error] {e}")
        return None

def init_db():
    """Initializes tables from schema.sql."""
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        for stmt in f.read().split(';'):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                try: cursor.execute(stmt)
                except Exception: pass
    conn.commit()
    cursor.close()
    conn.close()
