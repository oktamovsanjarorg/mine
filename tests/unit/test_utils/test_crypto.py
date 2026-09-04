import pytest
from src.core.utils.crypto import generate_password, hash_sha256, verify_hash, base64_encode, base64_decode

def test_generate_password():
    pwd = generate_password(12)
    assert len(pwd) == 12
    assert any(c.isupper() for c in pwd)
    assert any(c.islower() for c in pwd)
    assert any(c.isdigit() for c in pwd)

def test_hash_sha256():
    h = hash_sha256("test")
    assert len(h) == 64

def test_verify_hash():
    h = hash_sha256("secret")
    assert verify_hash("secret", h) is True
    assert verify_hash("wrong", h) is False

def test_base64():
    enc = base64_encode("salom")
    assert enc == "c2Fsb20="
    assert base64_decode(enc) == "salom"
