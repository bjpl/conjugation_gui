# Secure API Key Management Setup Guide

## Overview

This guide covers the secure API key management system for the Spanish Conjugation GUI, including setup, configuration, and best practices.

## 🚀 Quick Start

### First Run

1. **Launch the application** - The setup wizard will automatically appear on first run
2. **Choose your AI provider** - Currently supports OpenAI (more providers coming soon)
3. **Enter your API key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
4. **Select storage method** - The wizard will recommend the best option for your system
5. **Configure preferences** - Customize your learning experience

### Manual Setup

If you need to configure later or the automatic setup fails:

```bash
# Set environment variable (temporary)
export OPENAI_API_KEY="sk-your-api-key-here"

# Or create .env file
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

## 🔐 Security Features

### Storage Methods (in order of security)

1. **System Keyring** (Recommended)
   - Windows: Windows Credential Manager
   - macOS: Keychain
   - Linux: Secret Service (GNOME Keyring/KWallet)
   - Automatically encrypted by the OS
   - Integrated with system authentication

2. **Encrypted File Storage**
   - AES-256 encryption
   - Optional password protection
   - Stored in user configuration directory
   - Cross-platform compatibility

3. **Environment Variables** (Fallback)
   - Simple but less secure
   - Useful for development
   - Not recommended for production

### Security Validation

The system performs comprehensive validation:

- **Format checking** - Ensures API key format is correct
- **Live testing** - Verifies key works with API
- **Security scanning** - Detects common vulnerabilities
- **Entropy analysis** - Checks key randomness
- **Leak detection** - Identifies potentially compromised keys

## 📋 Configuration Options

### API Configuration

```json
{
  "api": {
    "provider": "openai",
    "model": "gpt-4o",
    "max_tokens": 600,
    "temperature": 0.5,
    "timeout": 30
  },
  "security": {
    "store_credentials_securely": true,
    "validate_api_keys": true,
    "encrypt_config": false,
    "audit_logging": true
  }
}
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `SPANISHCONJUGATIONGUI_API_MODEL` | AI model to use | `gpt-4o` |
| `SPANISHCONJUGATIONGUI_OFFLINE_MODE` | Enable offline mode | `true` |
| `SPANISHCONJUGATIONGUI_VALIDATE_KEYS` | Validate keys before storing | `true` |

## 🛠️ Advanced Setup

### Custom Configuration Directory

```python
from src.security import APIConfig

# Use custom directory
config = APIConfig(config_dir="/path/to/custom/dir")
```

### Programmatic API Key Management

```python
from src.security import CredentialsManager

manager = CredentialsManager()

# Store API key
manager.store_credential("openai_api_key", "sk-your-key-here")

# Retrieve API key
api_key = manager.retrieve_credential("openai_api_key")

# Validate API key
validation = manager.validate_credential("openai_api_key", api_key)
print(f"Valid: {validation['valid']}")
```

### Backup and Recovery

```python
from src.security import BackupManager

backup_mgr = BackupManager()

# Create backup
result = backup_mgr.create_backup("full", encrypt=True)

# List backups
backups = backup_mgr.list_backups()

# Restore from backup
result = backup_mgr.restore_backup("backup_name")
```

## 🔧 Troubleshooting

### Common Issues

**"Security modules not available"**
```bash
pip install keyring cryptography aiohttp
```

**"Keyring backend not found"**
- Windows: Ensure Windows Credential Manager is available
- Linux: Install `gnome-keyring` or `kwallet`
- macOS: Keychain should be available by default

**"API key validation failed"**
- Check API key format (should start with `sk-`)
- Verify key is active on OpenAI platform
- Check internet connection
- Ensure sufficient API credits

**"Permission denied" on Linux**
```bash
# Install keyring backend
sudo apt-get install gnome-keyring
# or
sudo apt-get install kwalletmanager

# Ensure session keyring is unlocked
```

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.getLogger('conjugation_gui.security').setLevel(logging.DEBUG)
```

### Manual Configuration Reset

If you need to start over:

```bash
# Remove configuration directory
rm -rf ~/.config/spanishconjugationgui/
# or on Windows
rmdir /s "%APPDATA%\\Local\\SpanishConjugationGUI\\"
```

## 🔐 Security Best Practices

### For Users

1. **Use System Keyring** - Always prefer system keyring when available
2. **Strong API Keys** - Never share or expose your API keys
3. **Regular Rotation** - Consider rotating API keys periodically
4. **Monitor Usage** - Check OpenAI usage dashboard regularly
5. **Secure Environment** - Keep your system updated and secure

### For Developers

1. **Never hardcode keys** - Always use secure storage
2. **Validate before storing** - Use built-in validation
3. **Audit logs** - Enable security logging
4. **Regular backups** - Backup configuration regularly
5. **Test fallbacks** - Ensure environment variable fallback works

## 📚 API Reference

### CredentialsManager

```python
class CredentialsManager:
    def store_credential(self, key: str, value: str) -> bool
    def retrieve_credential(self, key: str) -> Optional[str]
    def validate_credential(self, key: str, value: str) -> Dict[str, Any]
    def delete_credential(self, key: str) -> bool
    def list_credentials(self) -> List[str]
```

### APIConfig

```python
class APIConfig:
    def get_api_key(self, provider: str = None) -> Optional[str]
    def set_api_key(self, api_key: str, provider: str = None) -> bool
    def validate_api_key(self, api_key: str = None) -> Dict[str, Any]
    def test_api_key(self, api_key: str = None) -> Dict[str, Any]
```

### SetupWizard

```python
def run_setup_wizard(parent=None) -> bool
def check_first_run(app_name: str = "SpanishConjugationGUI") -> bool
```

## 🚨 Security Considerations

### Data Protection

- **Encryption**: All stored credentials use AES-256 encryption
- **Key Derivation**: Uses PBKDF2 with SHA-256 (100,000 iterations)
- **Access Control**: File permissions restricted to user only
- **Memory Safety**: Keys cleared from memory after use

### Network Security

- **TLS/SSL**: All API communications use HTTPS
- **Certificate Validation**: Full certificate chain validation
- **Timeout Protection**: Configurable request timeouts
- **Rate Limiting**: Built-in rate limiting for API tests

### Audit and Monitoring

- **Security Logging**: Comprehensive audit trails
- **Access Tracking**: Monitor credential access patterns
- **Validation History**: Track validation attempts
- **Backup Integrity**: Verify backup checksums

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Enable debug logging
3. Check system requirements
4. Consult the API documentation
5. File an issue with detailed logs

## 🔄 Migration Guide

### From Environment Variables

The new system automatically detects and imports existing environment variables. Your existing setup will continue working while providing enhanced security options.

### Upgrading

When upgrading, your existing configuration will be automatically migrated to the new secure format. Backups are created during migration.

---

**Remember**: Security is a shared responsibility. Keep your API keys safe, your system updated, and follow security best practices.