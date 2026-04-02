import os
from cryptography.fernet import Fernet

KEY_FILE = "secret.key"
EVIDENCE_FOLDER = "evidence_files"


def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)


def load_key():
    return open(KEY_FILE, "rb").read()


def encrypt_file(file_data, filename):

    if not os.path.exists(EVIDENCE_FOLDER):
        os.makedirs(EVIDENCE_FOLDER)

    key = load_key()
    fernet = Fernet(key)

    encrypted = fernet.encrypt(file_data)

    path = os.path.join(EVIDENCE_FOLDER, filename + ".enc")

    with open(path, "wb") as f:
        f.write(encrypted)

    return path


def decrypt_file(filepath):

    key = load_key()
    fernet = Fernet(key)

    with open(filepath, "rb") as f:
        encrypted = f.read()

    decrypted = fernet.decrypt(encrypted)

    return decrypted