from cryptography.fernet import Fernet
from app.config import get_settings

settings = get_settings()

class EncryptionHelper:
    """Handle encryption for sensitive data like backup codes"""
    
    def __init__(self):
        # Use encryption key from environment
        self.cipher = Fernet(settings.encryption_key.encode())
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext"""
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext"""
        return self.cipher.decrypt(ciphertext.encode()).decode()

# Singleton instance
encryption = EncryptionHelper()
