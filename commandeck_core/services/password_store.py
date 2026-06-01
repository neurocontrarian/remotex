"""Local password obfuscation using machine-id as key.

Not cryptographic protection — prevents casual reading of the config file.
The encoded password is only meaningful on the same OS install. The config
file is already chmod 600, so only the owning user can read it.

The key is derived from the platform-specific machine identifier:
  - Linux:   /etc/machine-id
  - macOS:   IOPlatformUUID
  - Windows: HKLM\\SOFTWARE\\Microsoft\\Cryptography\\MachineGuid

Reading /etc/machine-id directly (the previous behaviour) was unsafe on
macOS/Windows: the file does not exist, so every install fell back to
sha256(b'remotex-fallback') — an identical XOR key for every user, which
made encoded sudo passwords trivially decodable by anyone with read access
to the config file.
"""
import base64
import hashlib


def _key() -> bytes:
    try:
        from commandeck_core.platform import get_platform
        mid = get_platform().machine_id()
        if mid:
            return hashlib.sha256(mid.encode()).digest()
    except Exception:
        pass
    # Last-resort fallback if the platform adapter cannot resolve a
    # machine ID (should not happen in practice).
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
