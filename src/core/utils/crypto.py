import string
import secrets
import hashlib
import uuid
import base64

def generate_password(length: int = 16, include_special: bool = True) -> str:
    """Generate a secure random password guaranteeing uppercase, lowercase, and digit."""
    if length < 4:
        length = 4
    chars = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
    ]
    alphabet = string.ascii_letters + string.digits
    if include_special:
        chars.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
        alphabet += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    while len(chars) < length:
        chars.append(secrets.choice(alphabet))
        
    secrets.SystemRandom().shuffle(chars)
    return ''.join(chars[:length])

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

def verify_hash(data: str, hash_value: str) -> bool:
    """Verify data matches a SHA256 hash."""
    return hash_sha256(data) == hash_value

