from cryptography.fernet import Fernet
import base64
import hashlib
from ..config import settings

def _get_fernet_key() -> bytes:
    """Derive a valid 32-byte base64-encoded Fernet key from settings."""
    raw_key = settings.ENCRYPTION_KEY.encode()
    # If already 32 url-safe base64 bytes, check or derive using sha256
    try:
        # Check if valid 32 urlsafe base64 bytes
        decoded = base64.urlsafe_b64decode(raw_key)
        if len(decoded) == 32:
            return raw_key
    except Exception:
        pass
    
    # Derive 32 bytes using SHA-256 and base64-encode
    digest = hashlib.sha256(raw_key).digest()
    return base64.urlsafe_b64encode(digest)

_fernet_instance: Fernet = Fernet(_get_fernet_key())

def encrypt_data(plaintext: str) -> str:
    """Encrypt a string using Fernet symmetric encryption."""
    if not plaintext:
        return ""
    encrypted_bytes = _fernet_instance.encrypt(plaintext.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")

def decrypt_data(ciphertext: str) -> str:
    """Decrypt a Fernet encrypted string."""
    if not ciphertext:
        return ""
    decrypted_bytes = _fernet_instance.decrypt(ciphertext.encode("utf-8"))
    return decrypted_bytes.decode("utf-8")
