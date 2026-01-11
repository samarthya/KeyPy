"""TOTP (Time-based One-Time Password) support."""
import pyotp
from typing import Optional


class TOTPManager:
    """Manage TOTP tokens."""
    
    @staticmethod
    def generate_secret() -> str:
        """
        Generate a new TOTP secret.
        
        Returns:
            Base32-encoded secret
        """
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp_token(secret: str) -> str:
        """
        Generate a TOTP token from a secret.
        
        Args:
            secret: Base32-encoded secret
            
        Returns:
            6-digit TOTP token
        """
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    @staticmethod
    def verify_totp_token(secret: str, token: str) -> bool:
        """
        Verify a TOTP token.
        
        Args:
            secret: Base32-encoded secret
            token: Token to verify
            
        Returns:
            True if valid, False otherwise
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
    
    @staticmethod
    def get_provisioning_uri(secret: str, name: str, issuer: Optional[str] = None) -> str:
        """
        Get a provisioning URI for QR code generation.
        
        Args:
            secret: Base32-encoded secret
            name: Account name
            issuer: Optional issuer name
            
        Returns:
            Provisioning URI
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=name, issuer_name=issuer)
