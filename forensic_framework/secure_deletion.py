import os
import secrets

def secure_wipe(file_path, passes=3):
    """
    Overwrites the file with random data multiple times before deleting it.
    """
    if not os.path.exists(file_path):
        return False
    
    file_size = os.path.getsize(file_path)
    
    with open(file_path, "ba+", buffering=0) as f:
        for _ in range(passes):
            f.seek(0)
            f.write(secrets.token_bytes(file_size))
            f.flush()
            os.fsync(f.fileno())
            
    os.remove(file_path)
    return True
