import pytest
from app.utils.password_hasher import hash_password, verify_password


def test_hash_returns_string():
    result = hash_password("mysecretpassword")
    assert isinstance(result, str)
    assert len(result) > 0


def test_hash_is_not_plaintext():
    plain = "mysecretpassword"
    result = hash_password(plain)
    assert result != plain


def test_verify_correct_password_returns_true():
    plain = "correct-horse-battery-staple"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_wrong_password_returns_false():
    hashed = hash_password("correct_password")
    assert verify_password("wrong_password", hashed) is False


def test_two_hashes_of_same_password_differ():
    plain = "samepassword"
    hash1 = hash_password(plain)
    hash2 = hash_password(plain)
    assert hash1 != hash2  # bcrypt salting


def test_verify_both_hashes_of_same_password():
    plain = "samepassword"
    hash1 = hash_password(plain)
    hash2 = hash_password(plain)
    assert verify_password(plain, hash1) is True
    assert verify_password(plain, hash2) is True


def test_empty_password_hashes_and_verifies():
    plain = ""
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True
    assert verify_password("notempty", hashed) is False
