import sqlite3
import datetime

DATABASE = "database.db"

def log_action(evidence_id, action, officer):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    time = datetime.datetime.now()

    cursor.execute(
        "INSERT INTO custody (evidence_id, action, officer, time) VALUES (?,?,?,?)",
        (evidence_id, action, officer, time)
    )

    conn.commit()
    conn.close()