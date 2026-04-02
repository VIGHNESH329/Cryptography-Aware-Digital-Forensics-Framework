import hashlib
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

# Symmetric Encryption (AES equivalent via Fernet)
# Generate encryption key
key = Fernet.generate_key()
cipher = Fernet(key)


def generate_hash(data):
    """
    Generates a SHA256 hash. 
    If 'data' is a valid file path (str), it hashes the file contents.
    If 'data' is a string, it encodes it to bytes first.
    If 'data' is already bytes, it hashes directly.
    """
    sha = hashlib.sha256()
    if isinstance(data, str):
        if os.path.exists(data) and os.path.isfile(data):
            with open(data, 'rb') as f:
                while chunk := f.read(8192):
                    sha.update(chunk)
            return sha.hexdigest()
        data = data.encode()
    
    sha.update(data)
    return sha.hexdigest()


def encrypt_data(data):
    return cipher.encrypt(data)

# Asymmetric Encryption (RSA Digital Signatures)
def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

def sign_data(private_key, data):
    signature = private_key.sign(
        data,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return signature.hex()

def verify_signature(public_key, data, signature_hex):
    try:
        public_key.verify(
            bytes.fromhex(signature_hex),
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False