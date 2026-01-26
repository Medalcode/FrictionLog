import sqlite3
DB_PATH = "frictionlog.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fricciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        description TEXT,
        severity INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("DB initialized:", DB_PATH)
