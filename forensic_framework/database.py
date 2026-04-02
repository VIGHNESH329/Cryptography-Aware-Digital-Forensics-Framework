import sqlite3

def init_db():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT,
        filename TEXT,
        hash TEXT,
        signature TEXT,
        metadata TEXT,
        cloud_status TEXT DEFAULT 'Local',
        investigator TEXT,
        timestamp TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS custody(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evidence_id INTEGER,
        action TEXT,
        officer TEXT,
        time TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # Add default users if none exist
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'Auditor')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('detective1', 'pass123', 'Investigator')")

    conn.commit()
    conn.close()