from cryptography.fernet import Fernet
import base64
import os
import json
from datetime import datetime

class ConfigManager:
    def __init__(self, key=None):
        """Initialize with an encryption key or generate a new one"""
        if key:
            self.key = base64.urlsafe_b64encode(key.ljust(32)[:32].encode())
        else:
            self.key = base64.urlsafe_b64encode(os.urandom(32))
        self.cipher_suite = Fernet(self.key)
    
    def encrypt_credentials(self, credentials):
        """Encrypt credentials dictionary"""
        try:
            # Add timestamp for configuration tracking
            credentials['timestamp'] = datetime.now().isoformat()
            
            # Convert to JSON and encrypt
            json_data = json.dumps(credentials)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"Error encrypting credentials: {str(e)}")
            return None
    
    def decrypt_credentials(self, encrypted_data):
        """Decrypt credentials from encrypted string"""
        try:
            # Decode and decrypt
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            
            # Parse JSON
            credentials = json.loads(decrypted_data.decode())
            return credentials
        except Exception as e:
            print(f"Error decrypting credentials: {str(e)}")
            return None
    
    def export_config(self, credentials, filename):
        """Export encrypted configuration to file"""
        try:
            config_data = {
                'encrypted_credentials': self.encrypt_credentials(credentials),
                'export_date': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(filename, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting configuration: {str(e)}")
            return False
    
    def import_config(self, filename):
        """Import and decrypt configuration from file"""
        try:
            with open(filename, 'r') as f:
                config_data = json.load(f)
            
            if 'encrypted_credentials' not in config_data:
                raise ValueError("Invalid configuration file")
            
            return self.decrypt_credentials(config_data['encrypted_credentials'])
        except Exception as e:
            print(f"Error importing configuration: {str(e)}")
            return None
    
    def get_key(self):
        """Get the encryption key for storage"""
        return base64.urlsafe_b64encode(self.key).decode()
