"""Unit tests for bcrypt password hashing and verification.

Tests the password hashing and verification logic used in auth_routes.py
(bcrypt.hashpw / bcrypt.checkpw) without mocking bcrypt itself.
"""

import bcrypt
import pytest


def test_hashpw_returns_bytes():
    """hashpw produces a bytes result."""
    hashed = bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt())
    assert isinstance(hashed, bytes)


def test_hashpw_is_not_plaintext():
    """Hashed password is not equal to the original plaintext."""
    password = "supersecret"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    assert hashed != password.encode("utf-8")


def test_checkpw_correct_password_returns_true():
    """checkpw returns True when password matches stored hash."""
    password = "correct-password"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    assert bcrypt.checkpw(password.encode("utf-8"), hashed) is True


def test_checkpw_wrong_password_returns_false():
    """checkpw returns False when password does not match stored hash."""
    password = "correct-password"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    assert bcrypt.checkpw("wrong-password".encode("utf-8"), hashed) is False


def test_hashpw_uses_unique_salts():
    """Two hashes of the same password differ due to unique salts."""
    password = "same-password"
    hash1 = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    hash2 = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    assert hash1 != hash2


def test_hashpw_round_trip_with_decoded_hash():
    """checkpw works with a hash decoded from UTF-8 string (as stored in DB)."""
    password = "mypassword"
    hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    # auth_routes.py stores hashed_password as a UTF-8 string in the DB
    hashed_str = hashed_bytes.decode("utf-8")
    # When verifying, auth_routes.py re-encodes it: hashed_password.encode("utf-8")
    assert bcrypt.checkpw(password.encode("utf-8"), hashed_str.encode("utf-8")) is True


def test_checkpw_empty_password_against_hash_returns_false():
    """checkpw returns False for empty password checked against non-empty hash."""
    password = "nonempty"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    assert bcrypt.checkpw(b"", hashed) is False


def test_hashpw_handles_unicode_password():
    """bcrypt correctly hashes and verifies unicode passwords."""
    password = "pässwörd-ünïcödé"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    assert bcrypt.checkpw(password.encode("utf-8"), hashed) is True
    assert bcrypt.checkpw("wrong".encode("utf-8"), hashed) is False
