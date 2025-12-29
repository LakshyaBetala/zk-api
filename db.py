import sqlite3

DB_PATH = "attendance.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pin TEXT,
            name TEXT,
            time TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_log(pin, name, time, status):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO attendance (pin, name, time, status) VALUES (?, ?, ?, ?)",
        (pin, name, time, status)
    )
    conn.commit()
    conn.close()

def get_logs_by_date(date_str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT pin, name, time, status FROM attendance WHERE DATE(time)=?",
        (date_str,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows
