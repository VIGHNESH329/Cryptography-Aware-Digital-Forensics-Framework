import hashlib
import os
from crypto_utils import generate_hash

def check_tampering(stored_hash, file_path):
    if not os.path.exists(file_path):
        return "File Missing"
    
    new_hash = generate_hash(file_path)
    if stored_hash == new_hash:
        return "Verified"
    else:
        return "TAMPERED"