"""Tests for TOTP functionality."""
from keypy.utils.totp import TOTPManager


def test_generate_secret():
    """Test TOTP secret generation."""
    secret = TOTPManager.generate_secret()
    
    assert isinstance(secret, str)
    assert len(secret) > 0


def test_get_totp_token():
    """Test TOTP token generation."""
    secret = TOTPManager.generate_secret()
    token = TOTPManager.get_totp_token(secret)
    
    assert isinstance(token, str)
    assert len(token) == 6
    assert token.isdigit()


def test_verify_totp_token():
    """Test TOTP token verification."""
    secret = TOTPManager.generate_secret()
    token = TOTPManager.get_totp_token(secret)
    
    # Token should be valid
    assert TOTPManager.verify_totp_token(secret, token) is True
    
    # Wrong token should be invalid
    assert TOTPManager.verify_totp_token(secret, "000000") is False


def test_get_provisioning_uri():
    """Test provisioning URI generation."""
    secret = TOTPManager.generate_secret()
    uri = TOTPManager.get_provisioning_uri(secret, "test@example.com", "TestApp")
    
    assert isinstance(uri, str)
    assert uri.startswith("otpauth://totp/")
    # Email is URL-encoded in the URI
    assert "test%40example.com" in uri or "test@example.com" in uri
