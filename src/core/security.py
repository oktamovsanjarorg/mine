import hashlib
from cryptography.fernet import Fernet
from src.config import settings

def _get_fernet() -> Fernet:
    """Helper method to initialize Fernet with the configured key."""
    return Fernet(settings.fernet_key.encode('utf-8'))

def encrypt(data: str) -> str:
    """Encrypt a string using Fernet."""
    f = _get_fernet()
    encrypted_bytes = f.encrypt(data.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")

def decrypt(encrypted_data: str) -> str:
    """Decrypt a Fernet encrypted string."""
    f = _get_fernet()
    decrypted_bytes = f.decrypt(encrypted_data.encode("utf-8"))
    return decrypted_bytes.decode("utf-8")

def hash_sha256(data: str) -> str:
    """Hash a string using SHA256."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def verify_hash(data: str, hash_value: str) -> bool:
    """Verify a string against a SHA256 hash."""
    return hash_sha256(data) == hash_value
