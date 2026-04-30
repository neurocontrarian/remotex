"""Local password obfuscation using machine-id as key.

Not cryptographic protection — prevents casual reading of the config file.
The encoded password is only meaningful on the same OS install (same /etc/machine-id).
The config file is already chmod 600, so only the owning user can read it.
"""
import base64
import hashlib


def _key() -> bytes:
    try:
        with open('/etc/machine-id') as f:
            return hashlib.sha256(f.read().strip().encode()).digest()
    except OSError:
        return hashlib.sha256(b'remotex-fallback').digest()


def encode(password: str) -> str:
    key = _key()
    data = password.encode('utf-8')
    xored = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    return base64.urlsafe_b64encode(xored).decode()


def decode(encoded: str) -> str:
    try:
        key = _key()
        xored = base64.urlsafe_b64decode(encoded.encode())
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(xored)).decode('utf-8')
    except Exception:
        return ""
