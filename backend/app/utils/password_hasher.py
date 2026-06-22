import bcrypt

def hash_password(plain: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        plain: The raw password string provided by the user.

    Returns:
        A bcrypt hash string safe to store in the database.
    """
    # bcrypt requires bytes
    pwd_bytes = plain.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain:  The raw password to check.
        hashed: The stored bcrypt hash from the database.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    pwd_bytes = plain.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)
