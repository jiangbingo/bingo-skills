"""
Bingo Downloader Web - Cookie Encryption
Secure storage for browser cookies using Fernet encryption
"""
from pathlib import Path
from typing import Optional
import os
import base64
import hashlib

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Configuration
ENCRYPTION_KEY_ENV = os.getenv("COOKIE_ENCRYPTION_KEY", "")
COOKIES_CACHE_DIR = Path.home() / ".bingo-downloader" / "cookies"
ENCRYPTION_KEY_FILE = Path.home() / ".bingo-downloader" / ".encryption_key"

# Cookie expiration time (default: 1 day instead of 7 days)
COOKIE_EXPIRATION_HOURS = int(os.getenv("COOKIE_EXPIRATION_HOURS", "24"))

# Security warning
ENCRYPTION_WARNING = """
SECURITY NOTICE: Encrypted cookies are stored locally.
- Cookies expire after {hours} hours (configurable via COOKIE_EXPIRATION_HOURS)
- Encryption key is stored in {key_file}
- For production use, consider:
  * Using a secure key management service
  * Implementing proper secrets management
  * Regular security audits
"""


def generate_encryption_key(password: Optional[str] = None) -> bytes:
    """
    Generate or retrieve encryption key for cookie encryption.

    Args:
        password: Optional password for key generation.
                 If not provided, generates a random key.

    Returns:
        Fernet encryption key as bytes
    """
    # Check if key is provided via environment variable
    if ENCRYPTION_KEY_ENV:
        # Ensure the key is valid for Fernet (base64 encoded, 32 bytes)
        key_bytes = ENCRYPTION_KEY_ENV.encode()
        if len(key_bytes) < 32:
            # Pad with zeros if too short
            key_bytes = key_bytes.ljust(32, b"\x00")
        elif len(key_bytes) > 32:
            # Hash if too long
            key_bytes = hashlib.sha256(key_bytes).digest()

        # Encode to base64 for Fernet
        return base64.urlsafe_b64encode(key_bytes[:32])

    # Check if key file exists
    if ENCRYPTION_KEY_FILE.exists():
        with open(ENCRYPTION_KEY_FILE, "rb") as f:
            stored_key = f.read()
            try:
                # Validate key format
                base64.urlsafe_b64decode(stored_key)
                return stored_key
            except Exception:
                pass  # Key is invalid, generate new one

    # Generate new key
    COOKIES_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if password:
        # Derive key from password using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"bingo-downloader-salt",  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    else:
        # Generate random key
        key = Fernet.generate_key()

    # Save key to file
    ENCRYPTION_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ENCRYPTION_KEY_FILE, "wb") as f:
        f.write(key)

    # Set restrictive permissions
    ENCRYPTION_KEY_FILE.chmod(0o600)

    return key


def encrypt_data(data: str, key: Optional[bytes] = None) -> str:
    """
    Encrypt string data using Fernet symmetric encryption.

    Args:
        data: The string data to encrypt
        key: Optional encryption key. If not provided, generates/retrieves default key.

    Returns:
        Base64-encoded encrypted data

    Raises:
        RuntimeError: If cryptography module is not available
    """
    if not CRYPTO_AVAILABLE:
        raise RuntimeError(
            "cryptography module is required for cookie encryption. "
            "Install it with: pip install cryptography"
        )

    if key is None:
        key = generate_encryption_key()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str, key: Optional[bytes] = None) -> str:
    """
    Decrypt Fernet-encrypted data.

    Args:
        encrypted_data: Base64-encoded encrypted data
        key: Optional decryption key. If not provided, uses default key.

    Returns:
        Decrypted string data

    Raises:
        RuntimeError: If cryptography module is not available
        ValueError: If decryption fails (wrong key or corrupted data)
    """
    if not CRYPTO_AVAILABLE:
        raise RuntimeError(
            "cryptography module is required for cookie decryption. "
            "Install it with: pip install cryptography"
        )

    if key is None:
        key = generate_encryption_key()

    fernet = Fernet(key)
    try:
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        raise ValueError(f"Failed to decrypt data: {e}")


def get_encryption_status() -> dict:
    """
    Get the current encryption status and configuration.

    Returns:
        Dictionary with encryption status information
    """
    return {
        "encryption_enabled": CRYPTO_AVAILABLE,
        "key_from_env": bool(ENCRYPTION_KEY_ENV),
        "key_file_exists": ENCRYPTION_KEY_FILE.exists(),
        "cookie_expiration_hours": COOKIE_EXPIRATION_HOURS,
        "warning": ENCRYPTION_WARNING.format(
            hours=COOKIE_EXPIRATION_HOURS,
            key_file=str(ENCRYPTION_KEY_FILE)
        ) if CRYPTO_AVAILABLE else "cryptography module not installed. Install with: pip install cryptography",
    }


def is_encrypted_file(filepath: Path) -> bool:
    """
    Check if a file contains encrypted data.

    Args:
        filepath: Path to the file to check

    Returns:
        True if file appears to contain encrypted data
    """
    if not filepath.exists():
        return False

    try:
        with open(filepath, "r") as f:
            first_line = f.readline().strip()
            # Encrypted data is base64, check if it looks like base64
            # and doesn't look like plain text cookies
            if len(first_line) > 44:  # Minimum Fernet token length
                try:
                    # Try to decode as base64
                    decoded = base64.urlsafe_b64decode(first_line)
                    # Fernet tokens start with specific version byte (0x80)
                    return decoded[0] == 0x80 if len(decoded) > 0 else False
                except Exception:
                    return False
    except Exception:
        pass

    return False
