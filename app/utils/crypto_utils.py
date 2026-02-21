import os
import base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend


def hash_password(password: str) -> str:
    """Securely hash password using Scrypt."""

    salt = os.urandom(16)  # ✅ random salt

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )

    key = kdf.derive(password.encode())

    return base64.b64encode(salt + key).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""

    decoded = base64.b64decode(hashed_password)
    salt = decoded[:16]
    stored_key = decoded[16:]

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )

    try:
        kdf.verify(plain_password.encode(), stored_key)
        return True
    except Exception:
        return False