"""
Security Module for Spanish Conjugation GUI
==========================================

This module provides comprehensive security features for the Spanish Conjugation GUI,
including secure credential storage, API key management, and configuration security.

Components:
- CredentialsManager: Secure storage and retrieval of API keys and credentials
- APIConfig: Configuration management with security integration
- SetupWizard: First-run setup wizard for secure configuration

Author: Brand
Version: 1.0.0
"""

from .credentials_manager import (
    CredentialsManager, 
    CredentialsError, 
    KeyringUnavailableError, 
    EncryptionError, 
    ValidationError
)

from .api_config import (
    APIConfig,
    ConfigError,
    ConfigValidationError
)

from .setup_wizard import (
    SetupWizard,
    run_setup_wizard,
    check_first_run
)

__all__ = [
    # Credentials Management
    'CredentialsManager',
    'CredentialsError',
    'KeyringUnavailableError', 
    'EncryptionError',
    'ValidationError',
    
    # Configuration Management
    'APIConfig',
    'ConfigError',
    'ConfigValidationError',
    
    # Setup Wizard
    'SetupWizard',
    'run_setup_wizard',
    'check_first_run'
]

__version__ = '1.0.0'