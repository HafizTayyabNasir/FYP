"""
Fernet encryption for securing OAuth tokens and SMTP passwords at rest.
Generates a key automatically if ENCRYPTION_KEY is not set in .env.
"""
import base64
import hashlib
import logging

from cryptography.fernet import Fernet

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_fernet() -> Fernet:
    """
    Build a Fernet instance.
    - If ENCRYPTION_KEY is set in .env, use it directly.
    - Otherwise, derive a key from SECRET_KEY (always available).
    """
    raw_key = getattr(settings, "ENCRYPTION_KEY", None)
    if raw_key:
        return Fernet(raw_key.encode())

    # Derive a 32-byte key from SECRET_KEY using SHA-256
    digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


_fernet = _get_fernet()


def encrypt(plaintext: str) -> str:
    """Encrypt a string and return base64-encoded ciphertext."""
    if not plaintext:
        return ""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a base64-encoded ciphertext back to plaintext."""
    if not ciphertext:
        return ""
    return _fernet.decrypt(ciphertext.encode()).decode()
