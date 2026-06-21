from passlib.context import CryptContext  # type: ignore

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        plain: The raw password string provided by the user.

    Returns:
        A bcrypt hash string safe to store in the database.
    """
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain:  The raw password to check.
        hashed: The stored bcrypt hash from the database.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    return _pwd_context.verify(plain, hashed)
