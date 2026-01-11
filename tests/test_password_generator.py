"""Tests for password generator."""
import pytest
from keypy.core.password_generator import PasswordGenerator


def test_generate_password_default():
    """Test default password generation."""
    gen = PasswordGenerator()
    password = gen.generate()
    
    assert len(password) == 16
    assert isinstance(password, str)


def test_generate_password_length():
    """Test password generation with custom length."""
    gen = PasswordGenerator()
    password = gen.generate(length=32)
    
    assert len(password) == 32


def test_generate_password_character_sets():
    """Test password generation with different character sets."""
    gen = PasswordGenerator()
    
    # Only lowercase
    password = gen.generate(
        use_lowercase=True,
        use_uppercase=False,
        use_digits=False,
        use_special=False
    )
    assert password.islower()
    
    # Only uppercase
    password = gen.generate(
        use_lowercase=False,
        use_uppercase=True,
        use_digits=False,
        use_special=False
    )
    assert password.isupper()
    
    # Only digits
    password = gen.generate(
        use_lowercase=False,
        use_uppercase=False,
        use_digits=True,
        use_special=False
    )
    assert password.isdigit()


def test_generate_password_no_charset():
    """Test that error is raised when no character set is selected."""
    gen = PasswordGenerator()
    
    with pytest.raises(ValueError):
        gen.generate(
            use_lowercase=False,
            use_uppercase=False,
            use_digits=False,
            use_special=False
        )


def test_generate_passphrase():
    """Test passphrase generation."""
    gen = PasswordGenerator()
    passphrase = gen.generate_passphrase(word_count=5, separator="-")
    
    words = passphrase.split("-")
    assert len(words) == 5


def test_calculate_entropy():
    """Test entropy calculation."""
    gen = PasswordGenerator()
    
    # Simple password
    entropy = gen.calculate_entropy("abc123")
    assert entropy > 0
    
    # Complex password
    entropy_complex = gen.calculate_entropy("Abc123!@#")
    assert entropy_complex > entropy


def test_assess_strength():
    """Test password strength assessment."""
    gen = PasswordGenerator()
    
    # Weak password
    result = gen.assess_strength("abc")
    assert result['score'] <= 2
    assert result['strength'] in ['Very Weak', 'Weak']
    
    # Strong password
    result = gen.assess_strength("Abc123!@#XyzPoiQwe987")
    assert result['score'] >= 4
    assert result['strength'] in ['Strong', 'Very Strong']
