import os
import sqlite3
from crypto_utils import generate_hash, encrypt_file

DATABASE = "database.db"

def store_evidence(file):

    filename = file.filename
    path = os.path.join("evidence_storage", filename)

    file.save(path)

    hash_value = generate_hash(path)

    encrypted = encrypt_file(path)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO evidence (filename, hash) VALUES (?,?)",
        (filename, hash_value)
    )

    conn.commit()
    conn.close()

    return hash_value