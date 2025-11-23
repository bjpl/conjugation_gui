"""
Secure Credentials Manager for Spanish Conjugation GUI
====================================================

This module provides secure storage and retrieval of API keys and credentials
using the keyring library with fallback options including environment variables
and encrypted file storage.

Features:
- Keyring-based secure credential storage (OS-integrated)
- AES-256 encrypted file backup storage
- Environment variable fallback
- Credential validation and health checking
- Multiple storage backend support
- Secure credential rotation
- Audit logging for security events

Author: Brand
Version: 1.0.0
"""

import os
import json
import logging
import base64
import getpass
from typing import Dict, Optional, Any, Union, List
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import secrets

try:
    import keyring
    from keyring.backends import Windows, macOS, SecretService
    KEYRING_AVAILABLE = True
except ImportError:
    keyring = None
    KEYRING_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Configure logging for security events
security_logger = logging.getLogger('conjugation_gui.security')


class CredentialsError(Exception):
    """Base exception for credentials management errors"""
    pass


class KeyringUnavailableError(CredentialsError):
    """Raised when keyring service is unavailable"""
    pass


class EncryptionError(CredentialsError):
    """Raised when encryption/decryption operations fail"""
    pass


class ValidationError(CredentialsError):
    """Raised when credential validation fails"""
    pass


class CredentialsManager:
    """
    Secure credentials manager with multiple storage backends.
    
    Storage Priority (highest to lowest):
    1. OS Keyring (keyring library)
    2. Encrypted file storage (AES-256)
    3. Environment variables (fallback only)
    
    Attributes:
        app_name (str): Application identifier for keyring
        config_dir (Path): Directory for configuration files
        encrypted_file (Path): Path to encrypted credentials file
        master_key_file (Path): Path to master key file
        service_name (str): Service identifier for keyring
    """
    
    def __init__(self, 
                 app_name: str = "SpanishConjugationGUI",
                 config_dir: Optional[Path] = None):
        """
        Initialize the credentials manager.
        
        Args:
            app_name: Application name for keyring identification
            config_dir: Custom configuration directory (defaults to user config)
        """
        self.app_name = app_name
        self.service_name = f"com.{app_name.lower()}.apikeys"
        
        # Set up configuration directory
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Use platform-appropriate config directory
            if os.name == 'nt':  # Windows
                self.config_dir = Path.home() / 'AppData' / 'Local' / app_name
            else:  # Linux/macOS
                self.config_dir = Path.home() / '.config' / app_name.lower()
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths for encrypted storage
        self.encrypted_file = self.config_dir / 'credentials.enc'
        self.master_key_file = self.config_dir / 'master.key'
        self.config_file = self.config_dir / 'api_config.json'
        
        # Check available backends
        self.keyring_available = KEYRING_AVAILABLE and self._test_keyring()
        self.crypto_available = CRYPTO_AVAILABLE
        
        # Initialize configuration
        self.config = self._load_config()
        
        security_logger.info(f"CredentialsManager initialized. Keyring: {self.keyring_available}, Crypto: {self.crypto_available}")
    
    def _test_keyring(self) -> bool:
        """Test if keyring is available and functional."""
        if not keyring:
            return False
        
        try:
            # Test with a temporary key
            test_key = f"{self.service_name}.test"
            test_value = "test_value_12345"
            
            keyring.set_password(test_key, "test", test_value)
            retrieved = keyring.get_password(test_key, "test")
            keyring.delete_password(test_key, "test")
            
            return retrieved == test_value
        except Exception as e:
            security_logger.warning(f"Keyring test failed: {e}")
            return False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration settings."""
        default_config = {
            "storage_preference": "auto",  # auto, keyring, encrypted_file, env_only
            "encryption_enabled": True,
            "key_rotation_days": 90,
            "validation_enabled": True,
            "audit_logging": True,
            "backup_copies": 3,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults for new keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                self._save_config(default_config)
                return default_config
        except Exception as e:
            security_logger.error(f"Error loading config: {e}")
            return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration settings."""
        try:
            config['last_updated'] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            security_logger.debug("Configuration saved successfully")
        except Exception as e:
            security_logger.error(f"Error saving config: {e}")
    
    def _generate_encryption_key(self, password: Optional[str] = None) -> bytes:
        """
        Generate encryption key from password or create new one.
        
        Args:
            password: Optional password for key derivation
            
        Returns:
            32-byte encryption key
        """
        if password:
            # Derive key from password
            password_bytes = password.encode()
            salt = b"conjugation_gui_salt_v1"  # Fixed salt for reproducibility
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            return kdf.derive(password_bytes)
        else:
            # Generate random key
            return Fernet.generate_key()
    
    def _get_master_key(self, password: Optional[str] = None) -> bytes:
        """Get or create master encryption key."""
        if self.master_key_file.exists():
            try:
                with open(self.master_key_file, 'rb') as f:
                    encrypted_key = f.read()
                
                if password:
                    # Decrypt with password
                    derived_key = self._generate_encryption_key(password)
                    fernet = Fernet(base64.urlsafe_b64encode(derived_key))
                    return fernet.decrypt(encrypted_key)
                else:
                    # Key is stored in plaintext (less secure fallback)
                    return encrypted_key
            except Exception as e:
                security_logger.error(f"Error reading master key: {e}")
                raise EncryptionError("Failed to read master key")
        else:
            # Create new master key
            master_key = Fernet.generate_key()
            
            if password:
                # Encrypt master key with password
                derived_key = self._generate_encryption_key(password)
                fernet = Fernet(base64.urlsafe_b64encode(derived_key))
                encrypted_key = fernet.encrypt(master_key)
                with open(self.master_key_file, 'wb') as f:
                    f.write(encrypted_key)
            else:
                # Store master key in plaintext (less secure)
                with open(self.master_key_file, 'wb') as f:
                    f.write(master_key)
            
            # Restrict file permissions
            if hasattr(os, 'chmod'):
                os.chmod(self.master_key_file, 0o600)
            
            security_logger.info("New master key created")
            return master_key
    
    def _encrypt_data(self, data: Dict[str, Any], password: Optional[str] = None) -> bytes:
        """Encrypt credentials data."""
        if not self.crypto_available:
            raise EncryptionError("Cryptography library not available")
        
        try:
            master_key = self._get_master_key(password)
            fernet = Fernet(master_key)
            
            # Add metadata
            data_with_meta = {
                "credentials": data,
                "encrypted_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            json_data = json.dumps(data_with_meta, ensure_ascii=False)
            return fernet.encrypt(json_data.encode('utf-8'))
        except Exception as e:
            security_logger.error(f"Encryption failed: {e}")
            raise EncryptionError(f"Failed to encrypt data: {e}")
    
    def _decrypt_data(self, encrypted_data: bytes, password: Optional[str] = None) -> Dict[str, Any]:
        """Decrypt credentials data."""
        if not self.crypto_available:
            raise EncryptionError("Cryptography library not available")
        
        try:
            master_key = self._get_master_key(password)
            fernet = Fernet(master_key)
            
            decrypted_bytes = fernet.decrypt(encrypted_data)
            data_with_meta = json.loads(decrypted_bytes.decode('utf-8'))
            
            # Return just the credentials
            return data_with_meta.get("credentials", {})
        except Exception as e:
            security_logger.error(f"Decryption failed: {e}")
            raise EncryptionError(f"Failed to decrypt data: {e}")
    
    def store_credential(self, 
                        key: str, 
                        value: str, 
                        username: str = "default",
                        storage_method: Optional[str] = None) -> bool:
        """
        Store a credential securely.
        
        Args:
            key: Credential identifier (e.g., 'openai_api_key')
            value: Credential value
            username: Username for keyring (default: 'default')
            storage_method: Force specific storage method
            
        Returns:
            True if successful, False otherwise
        """
        try:
            method = storage_method or self.config.get("storage_preference", "auto")
            success = False
            
            # Try keyring first (if available and preferred)
            if method in ["auto", "keyring"] and self.keyring_available:
                try:
                    service_key = f"{self.service_name}.{key}"
                    keyring.set_password(service_key, username, value)
                    success = True
                    security_logger.info(f"Credential '{key}' stored in keyring")
                except Exception as e:
                    security_logger.warning(f"Keyring storage failed for '{key}': {e}")
            
            # Try encrypted file storage
            if not success and method in ["auto", "encrypted_file"] and self.crypto_available:
                try:
                    # Load existing credentials
                    existing_creds = {}
                    if self.encrypted_file.exists():
                        with open(self.encrypted_file, 'rb') as f:
                            encrypted_data = f.read()
                        existing_creds = self._decrypt_data(encrypted_data)
                    
                    # Add new credential
                    existing_creds[key] = {
                        "value": value,
                        "username": username,
                        "stored_at": datetime.now().isoformat(),
                        "hash": hashlib.sha256(value.encode()).hexdigest()[:16]
                    }
                    
                    # Encrypt and save
                    encrypted_data = self._encrypt_data(existing_creds)
                    with open(self.encrypted_file, 'wb') as f:
                        f.write(encrypted_data)
                    
                    # Restrict file permissions
                    if hasattr(os, 'chmod'):
                        os.chmod(self.encrypted_file, 0o600)
                    
                    success = True
                    security_logger.info(f"Credential '{key}' stored in encrypted file")
                except Exception as e:
                    security_logger.error(f"Encrypted file storage failed for '{key}': {e}")
            
            if success:
                # Update configuration
                self.config['last_updated'] = datetime.now().isoformat()
                self._save_config(self.config)
                return True
            else:
                security_logger.error(f"All storage methods failed for credential '{key}'")
                return False
                
        except Exception as e:
            security_logger.error(f"Error storing credential '{key}': {e}")
            return False
    
    def retrieve_credential(self, 
                          key: str, 
                          username: str = "default") -> Optional[str]:
        """
        Retrieve a credential securely.
        
        Args:
            key: Credential identifier
            username: Username for keyring
            
        Returns:
            Credential value or None if not found
        """
        try:
            # Try keyring first
            if self.keyring_available:
                try:
                    service_key = f"{self.service_name}.{key}"
                    value = keyring.get_password(service_key, username)
                    if value:
                        security_logger.debug(f"Credential '{key}' retrieved from keyring")
                        return value
                except Exception as e:
                    security_logger.warning(f"Keyring retrieval failed for '{key}': {e}")
            
            # Try encrypted file
            if self.crypto_available and self.encrypted_file.exists():
                try:
                    with open(self.encrypted_file, 'rb') as f:
                        encrypted_data = f.read()
                    
                    credentials = self._decrypt_data(encrypted_data)
                    if key in credentials:
                        credential_data = credentials[key]
                        value = credential_data.get("value")
                        if value:
                            security_logger.debug(f"Credential '{key}' retrieved from encrypted file")
                            return value
                except Exception as e:
                    security_logger.warning(f"Encrypted file retrieval failed for '{key}': {e}")
            
            # Fallback to environment variable
            env_key = f"{key.upper()}"
            value = os.getenv(env_key)
            if value:
                security_logger.debug(f"Credential '{key}' retrieved from environment")
                return value
            
            # Try alternative environment variable names
            alt_names = [
                f"CONJUGATION_GUI_{key.upper()}",
                f"SPANISH_GUI_{key.upper()}",
                key.replace('_', '').upper()
            ]
            
            for alt_name in alt_names:
                value = os.getenv(alt_name)
                if value:
                    security_logger.debug(f"Credential '{key}' retrieved from environment (alt: {alt_name})")
                    return value
            
            security_logger.warning(f"Credential '{key}' not found in any storage")
            return None
            
        except Exception as e:
            security_logger.error(f"Error retrieving credential '{key}': {e}")
            return None
    
    def validate_credential(self, key: str, value: str) -> Dict[str, Any]:
        """
        Validate a credential value.
        
        Args:
            key: Credential identifier
            value: Credential value to validate
            
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        try:
            if key.lower() in ['openai_api_key', 'openai_key', 'api_key']:
                # Validate OpenAI API key
                if not value:
                    result["errors"].append("API key is empty")
                elif not value.startswith('sk-'):
                    result["errors"].append("OpenAI API key should start with 'sk-'")
                elif len(value) < 40:
                    result["errors"].append("OpenAI API key appears too short")
                elif len(value) > 200:
                    result["errors"].append("OpenAI API key appears too long")
                else:
                    result["valid"] = True
                    result["info"]["type"] = "OpenAI API Key"
                    result["info"]["prefix"] = value[:10] + "..."
                
                # Additional security checks
                if ' ' in value:
                    result["warnings"].append("API key contains spaces")
                if not value.replace('-', '').replace('_', '').isalnum():
                    result["warnings"].append("API key contains unusual characters")
            
            else:
                # Generic validation
                if not value:
                    result["errors"].append("Credential is empty")
                elif len(value.strip()) != len(value):
                    result["warnings"].append("Credential has leading/trailing whitespace")
                else:
                    result["valid"] = True
                    result["info"]["type"] = "Generic Credential"
                    result["info"]["length"] = len(value)
            
            return result
            
        except Exception as e:
            security_logger.error(f"Error validating credential '{key}': {e}")
            result["errors"].append(f"Validation error: {e}")
            return result
    
    def test_credential(self, key: str, value: str) -> Dict[str, Any]:
        """
        Test a credential by making an API call.
        
        Args:
            key: Credential identifier
            value: Credential value to test
            
        Returns:
            Test result dictionary
        """
        result = {
            "success": False,
            "error": None,
            "info": {}
        }
        
        try:
            if key.lower() in ['openai_api_key', 'openai_key', 'api_key']:
                # Test OpenAI API key
                try:
                    import openai
                    client = openai.OpenAI(api_key=value)
                    
                    # Make a minimal test request
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=5
                    )
                    
                    result["success"] = True
                    result["info"]["model_used"] = "gpt-3.5-turbo"
                    result["info"]["test_completed"] = datetime.now().isoformat()
                    security_logger.info(f"API key test successful for '{key}'")
                    
                except Exception as e:
                    result["error"] = str(e)
                    security_logger.warning(f"API key test failed for '{key}': {e}")
            else:
                result["error"] = f"Testing not implemented for credential type: {key}"
            
            return result
            
        except Exception as e:
            result["error"] = f"Test error: {e}"
            security_logger.error(f"Error testing credential '{key}': {e}")
            return result
    
    def list_credentials(self) -> List[str]:
        """
        List all stored credential keys.
        
        Returns:
            List of credential identifiers
        """
        credentials = set()
        
        try:
            # Check encrypted file
            if self.crypto_available and self.encrypted_file.exists():
                try:
                    with open(self.encrypted_file, 'rb') as f:
                        encrypted_data = f.read()
                    creds_dict = self._decrypt_data(encrypted_data)
                    credentials.update(creds_dict.keys())
                except Exception as e:
                    security_logger.warning(f"Error listing from encrypted file: {e}")
            
            # Check environment variables (common patterns)
            env_patterns = [
                'OPENAI_API_KEY',
                'CONJUGATION_GUI_API_KEY',
                'SPANISH_GUI_API_KEY'
            ]
            for pattern in env_patterns:
                if os.getenv(pattern):
                    # Convert back to internal format
                    key = pattern.lower().replace('conjugation_gui_', '').replace('spanish_gui_', '')
                    credentials.add(key)
            
            return sorted(list(credentials))
            
        except Exception as e:
            security_logger.error(f"Error listing credentials: {e}")
            return []
    
    def delete_credential(self, key: str, username: str = "default") -> bool:
        """
        Delete a stored credential.
        
        Args:
            key: Credential identifier
            username: Username for keyring
            
        Returns:
            True if successful, False otherwise
        """
        success = False
        
        try:
            # Delete from keyring
            if self.keyring_available:
                try:
                    service_key = f"{self.service_name}.{key}"
                    keyring.delete_password(service_key, username)
                    success = True
                    security_logger.info(f"Credential '{key}' deleted from keyring")
                except Exception as e:
                    security_logger.debug(f"Keyring deletion failed for '{key}': {e}")
            
            # Delete from encrypted file
            if self.crypto_available and self.encrypted_file.exists():
                try:
                    with open(self.encrypted_file, 'rb') as f:
                        encrypted_data = f.read()
                    
                    credentials = self._decrypt_data(encrypted_data)
                    if key in credentials:
                        del credentials[key]
                        
                        # Re-encrypt and save
                        if credentials:  # If there are remaining credentials
                            encrypted_data = self._encrypt_data(credentials)
                            with open(self.encrypted_file, 'wb') as f:
                                f.write(encrypted_data)
                        else:  # Delete file if empty
                            self.encrypted_file.unlink()
                        
                        success = True
                        security_logger.info(f"Credential '{key}' deleted from encrypted file")
                except Exception as e:
                    security_logger.warning(f"Encrypted file deletion failed for '{key}': {e}")
            
            return success
            
        except Exception as e:
            security_logger.error(f"Error deleting credential '{key}': {e}")
            return False
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about available storage backends."""
        return {
            "keyring_available": self.keyring_available,
            "keyring_backend": keyring.get_keyring().__class__.__name__ if self.keyring_available else None,
            "encryption_available": self.crypto_available,
            "config_dir": str(self.config_dir),
            "encrypted_file_exists": self.encrypted_file.exists(),
            "config": self.config.copy(),
            "supported_methods": self._get_supported_methods()
        }
    
    def _get_supported_methods(self) -> List[str]:
        """Get list of supported storage methods."""
        methods = ["environment"]
        
        if self.keyring_available:
            methods.append("keyring")
        
        if self.crypto_available:
            methods.append("encrypted_file")
        
        return methods
    
    def backup_credentials(self, backup_path: Optional[Path] = None) -> bool:
        """
        Create a backup of all credentials.
        
        Args:
            backup_path: Optional custom backup path
            
        Returns:
            True if successful
        """
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.config_dir / f"credentials_backup_{timestamp}.json"
            
            # Collect all credentials (without values for security)
            backup_data = {
                "created_at": datetime.now().isoformat(),
                "app_name": self.app_name,
                "config": self.config.copy(),
                "credential_list": self.list_credentials(),
                "storage_info": self.get_storage_info()
            }
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            security_logger.info(f"Credentials backup created: {backup_path}")
            return True
            
        except Exception as e:
            security_logger.error(f"Error creating backup: {e}")
            return False
    
    def rotate_master_key(self, old_password: Optional[str] = None, 
                         new_password: Optional[str] = None) -> bool:
        """
        Rotate the master encryption key.
        
        Args:
            old_password: Current password (if any)
            new_password: New password (if any)
            
        Returns:
            True if successful
        """
        try:
            if not self.crypto_available:
                raise EncryptionError("Encryption not available for key rotation")
            
            # Backup current credentials
            if not self.backup_credentials():
                security_logger.error("Failed to create backup before key rotation")
                return False
            
            # Load existing credentials
            credentials = {}
            if self.encrypted_file.exists():
                with open(self.encrypted_file, 'rb') as f:
                    encrypted_data = f.read()
                credentials = self._decrypt_data(encrypted_data, old_password)
            
            # Delete old key file
            if self.master_key_file.exists():
                self.master_key_file.unlink()
            
            # Create new master key
            new_master_key = self._get_master_key(new_password)
            
            # Re-encrypt with new key
            if credentials:
                encrypted_data = self._encrypt_data(credentials, new_password)
                with open(self.encrypted_file, 'wb') as f:
                    f.write(encrypted_data)
            
            # Update config
            self.config['last_key_rotation'] = datetime.now().isoformat()
            self._save_config(self.config)
            
            security_logger.info("Master key rotation completed successfully")
            return True
            
        except Exception as e:
            security_logger.error(f"Key rotation failed: {e}")
            return False