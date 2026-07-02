"""Lightweight username/password auth: PBKDF2 password hashing and opaque
bearer tokens backed by a sessions table. No external dependency needed."""
import hashlib
import secrets

_PBKDF2_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _PBKDF2_ITERATIONS
    ).hex()
    return f"{salt}:{digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split(":", 1)
    except ValueError:
        return False
    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _PBKDF2_ITERATIONS
    ).hex()
    return secrets.compare_digest(candidate, digest)


def generate_token() -> str:
    return secrets.token_urlsafe(32)
