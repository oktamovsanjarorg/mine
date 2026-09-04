import string
import secrets
import hashlib
import uuid
import base64

def generate_password(length: int = 16, include_special: bool = True) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits
    if include_special:
        alphabet += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for i in range(length))

def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())

def hash_md5(data: str) -> str:
    """Create MD5 hash of a string."""
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def hash_sha256(data: str) -> str:
    """Create SHA256 hash of a string."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def hash_sha512(data: str) -> str:
    """Create SHA512 hash of a string."""
    return hashlib.sha512(data.encode('utf-8')).hexdigest()

def base64_encode(data: str) -> str:
    """Base64 encode a string."""
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')

def base64_decode(data: str) -> str:
    """Base64 decode a string."""
    return base64.b64decode(data.encode('utf-8')).decode('utf-8')
