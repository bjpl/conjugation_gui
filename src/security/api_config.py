"""
API Configuration Management for Spanish Conjugation GUI
======================================================

This module provides configuration management for API keys and settings,
integrating with the secure credentials manager and providing a unified
interface for API configuration.

Features:
- INI and JSON configuration file support
- Integration with secure credential storage
- Configuration validation and migration
- Environment-specific settings
- Configuration templates and defaults
- Auto-discovery of configuration files

Author: Brand
Version: 1.0.0
"""

import os
import json
import configparser
import logging
from typing import Dict, Optional, Any, List, Union
from pathlib import Path
from datetime import datetime

from .credentials_manager import CredentialsManager, CredentialsError


class ConfigError(Exception):
    """Base exception for configuration errors"""
    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails"""
    pass


class APIConfig:
    """
    API Configuration manager with secure credential integration.
    
    Supports multiple configuration formats:
    - JSON (.json)
    - INI (.ini, .cfg)
    - Environment variables
    
    Configuration hierarchy (highest to lowest priority):
    1. Environment variables
    2. User configuration file
    3. System configuration file
    4. Default configuration
    """
    
    def __init__(self, 
                 app_name: str = "SpanishConjugationGUI",
                 config_dir: Optional[Path] = None):
        """
        Initialize API configuration manager.
        
        Args:
            app_name: Application name for configuration
            config_dir: Custom configuration directory
        """
        self.app_name = app_name
        self.logger = logging.getLogger(f'{app_name}.config')
        
        # Initialize credentials manager
        self.credentials_manager = CredentialsManager(app_name, config_dir)
        
        # Configuration directory
        self.config_dir = self.credentials_manager.config_dir
        
        # Configuration file paths
        self.json_config_file = self.config_dir / 'api_config.json'
        self.ini_config_file = self.config_dir / 'api_config.ini'
        self.user_config_file = self.config_dir / 'user_config.json'
        
        # System config paths
        self.system_config_paths = self._get_system_config_paths()
        
        # Default configuration
        self.default_config = self._get_default_config()
        
        # Load configuration
        self.config = self._load_configuration()
        
        self.logger.info("API Configuration initialized")
    
    def _get_system_config_paths(self) -> List[Path]:
        """Get system-wide configuration paths."""
        paths = []
        
        if os.name == 'nt':  # Windows
            # Check Program Files and ProgramData
            for base in [Path('C:/ProgramData'), Path('C:/Program Files')]:
                paths.append(base / self.app_name / 'config.json')
                paths.append(base / self.app_name / 'config.ini')
        else:  # Linux/macOS
            # Check /etc and /usr/local/etc
            for base in [Path('/etc'), Path('/usr/local/etc')]:
                paths.append(base / self.app_name.lower() / 'config.json')
                paths.append(base / self.app_name.lower() / 'config.ini')
        
        return [p for p in paths if p.exists()]
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            # API Configuration
            "api": {
                "provider": "openai",
                "model": "gpt-4o",
                "max_tokens": 600,
                "temperature": 0.5,
                "timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 1.0
            },
            
            # Security Settings
            "security": {
                "store_credentials_securely": True,
                "validate_api_keys": True,
                "encrypt_config": False,
                "require_authentication": False
            },
            
            # Application Settings
            "app": {
                "version": "1.0.0",
                "debug_mode": False,
                "log_level": "INFO",
                "auto_update": True,
                "backup_settings": True
            },
            
            # Features
            "features": {
                "offline_mode": True,
                "dark_mode": False,
                "show_translation": False,
                "exercise_count": 5,
                "answer_strictness": "normal"
            },
            
            # Paths and Directories
            "paths": {
                "data_dir": str(self.config_dir),
                "backup_dir": str(self.config_dir / 'backups'),
                "log_dir": str(self.config_dir / 'logs'),
                "cache_dir": str(self.config_dir / 'cache')
            },
            
            # Metadata
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "created_by": "APIConfig",
                "config_version": "1.0"
            }
        }
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration from all sources."""
        config = self.default_config.copy()
        
        # Load from system config files
        for system_path in self.system_config_paths:
            try:
                system_config = self._load_config_file(system_path)
                config = self._merge_configs(config, system_config)
                self.logger.debug(f"Loaded system config from {system_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load system config {system_path}: {e}")
        
        # Load from user config files (in order of preference)
        config_files = [
            self.json_config_file,
            self.user_config_file,
            self.ini_config_file
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    user_config = self._load_config_file(config_file)
                    config = self._merge_configs(config, user_config)
                    self.logger.debug(f"Loaded user config from {config_file}")
                    break
                except Exception as e:
                    self.logger.error(f"Failed to load config {config_file}: {e}")
        
        # Override with environment variables
        env_config = self._load_env_config()
        config = self._merge_configs(config, env_config)
        
        return config
    
    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from a file."""
        if not config_path.exists():
            return {}
        
        suffix = config_path.suffix.lower()
        
        if suffix == '.json':
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        elif suffix in ['.ini', '.cfg']:
            parser = configparser.ConfigParser()
            parser.read(config_path, encoding='utf-8')
            
            # Convert to nested dict structure
            config = {}
            for section_name in parser.sections():
                config[section_name] = {}
                for key, value in parser.items(section_name):
                    # Try to parse as JSON for complex values
                    try:
                        parsed_value = json.loads(value)
                    except:
                        # Handle boolean and numeric values
                        if value.lower() in ('true', 'yes', '1', 'on'):
                            parsed_value = True
                        elif value.lower() in ('false', 'no', '0', 'off'):
                            parsed_value = False
                        elif value.isdigit():
                            parsed_value = int(value)
                        elif self._is_float(value):
                            parsed_value = float(value)
                        else:
                            parsed_value = value
                    
                    config[section_name][key] = parsed_value
            
            return config
        
        else:
            raise ConfigError(f"Unsupported config file format: {suffix}")
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {}
        
        # Define environment variable mappings
        env_mappings = {
            # API settings
            f"{self.app_name.upper()}_API_PROVIDER": ("api", "provider"),
            f"{self.app_name.upper()}_API_MODEL": ("api", "model"),
            f"{self.app_name.upper()}_API_MAX_TOKENS": ("api", "max_tokens"),
            f"{self.app_name.upper()}_API_TEMPERATURE": ("api", "temperature"),
            f"{self.app_name.upper()}_API_TIMEOUT": ("api", "timeout"),
            
            # Common OpenAI variables
            "OPENAI_MODEL": ("api", "model"),
            "OPENAI_MAX_TOKENS": ("api", "max_tokens"),
            "OPENAI_TEMPERATURE": ("api", "temperature"),
            
            # Security settings
            f"{self.app_name.upper()}_VALIDATE_KEYS": ("security", "validate_api_keys"),
            f"{self.app_name.upper()}_ENCRYPT_CONFIG": ("security", "encrypt_config"),
            
            # App settings
            f"{self.app_name.upper()}_DEBUG": ("app", "debug_mode"),
            f"{self.app_name.upper()}_LOG_LEVEL": ("app", "log_level"),
            
            # Feature settings
            f"{self.app_name.upper()}_OFFLINE_MODE": ("features", "offline_mode"),
            f"{self.app_name.upper()}_DARK_MODE": ("features", "dark_mode"),
            f"{self.app_name.upper()}_SHOW_TRANSLATION": ("features", "show_translation"),
            f"{self.app_name.upper()}_EXERCISE_COUNT": ("features", "exercise_count")
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if section not in env_config:
                    env_config[section] = {}
                
                # Parse value
                parsed_value = self._parse_env_value(value)
                env_config[section][key] = parsed_value
        
        return env_config
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type."""
        # Try JSON first
        try:
            return json.loads(value)
        except:
            pass
        
        # Handle boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Handle numeric values
        if value.isdigit():
            return int(value)
        elif self._is_float(value):
            return float(value)
        
        # Return as string
        return value
    
    def _is_float(self, value: str) -> bool:
        """Check if string represents a float."""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path (e.g., 'api.model')
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        try:
            parts = key_path.split('.')
            value = self.config
            
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def set(self, key_path: str, value: Any, save: bool = True) -> bool:
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path
            value: Value to set
            save: Whether to save configuration to file
            
        Returns:
            True if successful
        """
        try:
            parts = key_path.split('.')
            config = self.config
            
            # Navigate to parent
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            
            # Set value
            config[parts[-1]] = value
            
            if save:
                return self.save_config()
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting config value {key_path}: {e}")
            return False
    
    def get_api_key(self, provider: str = None) -> Optional[str]:
        """
        Get API key for specified provider.
        
        Args:
            provider: API provider name (defaults to current provider)
            
        Returns:
            API key or None if not found
        """
        if not provider:
            provider = self.get('api.provider', 'openai')
        
        # Try to get from credentials manager
        key_names = [
            f"{provider}_api_key",
            f"{provider}_key",
            "api_key"
        ]
        
        for key_name in key_names:
            api_key = self.credentials_manager.retrieve_credential(key_name)
            if api_key:
                return api_key
        
        # Fallback to environment variables
        env_keys = [
            f"{provider.upper()}_API_KEY",
            f"{self.app_name.upper()}_{provider.upper()}_KEY",
            "OPENAI_API_KEY"  # Common fallback
        ]
        
        for env_key in env_keys:
            api_key = os.getenv(env_key)
            if api_key:
                return api_key
        
        return None
    
    def set_api_key(self, api_key: str, provider: str = None) -> bool:
        """
        Set API key for specified provider.
        
        Args:
            api_key: API key value
            provider: API provider name
            
        Returns:
            True if successful
        """
        if not provider:
            provider = self.get('api.provider', 'openai')
        
        key_name = f"{provider}_api_key"
        
        # Validate the key
        if self.get('security.validate_api_keys', True):
            validation = self.credentials_manager.validate_credential(key_name, api_key)
            if not validation['valid']:
                self.logger.error(f"API key validation failed: {validation['errors']}")
                return False
        
        # Store the key
        success = self.credentials_manager.store_credential(key_name, api_key)
        if success:
            self.logger.info(f"API key stored successfully for provider: {provider}")
        else:
            self.logger.error(f"Failed to store API key for provider: {provider}")
        
        return success
    
    def validate_api_key(self, api_key: str = None, provider: str = None) -> Dict[str, Any]:
        """
        Validate API key.
        
        Args:
            api_key: API key to validate (defaults to current key)
            provider: Provider name
            
        Returns:
            Validation result
        """
        if not api_key:
            api_key = self.get_api_key(provider)
        
        if not api_key:
            return {
                "valid": False,
                "errors": ["No API key found"],
                "warnings": [],
                "info": {}
            }
        
        if not provider:
            provider = self.get('api.provider', 'openai')
        
        key_name = f"{provider}_api_key"
        return self.credentials_manager.validate_credential(key_name, api_key)
    
    def test_api_key(self, api_key: str = None, provider: str = None) -> Dict[str, Any]:
        """
        Test API key by making a request.
        
        Args:
            api_key: API key to test
            provider: Provider name
            
        Returns:
            Test result
        """
        if not api_key:
            api_key = self.get_api_key(provider)
        
        if not api_key:
            return {
                "success": False,
                "error": "No API key found",
                "info": {}
            }
        
        if not provider:
            provider = self.get('api.provider', 'openai')
        
        key_name = f"{provider}_api_key"
        return self.credentials_manager.test_credential(key_name, api_key)
    
    def save_config(self, format: str = 'json') -> bool:
        """
        Save configuration to file.
        
        Args:
            format: Configuration format ('json' or 'ini')
            
        Returns:
            True if successful
        """
        try:
            # Update metadata
            self.config['metadata']['last_updated'] = datetime.now().isoformat()
            
            if format.lower() == 'json':
                with open(self.json_config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                    
            elif format.lower() == 'ini':
                parser = configparser.ConfigParser()
                
                # Convert nested dict to INI format
                for section_name, section_data in self.config.items():
                    if isinstance(section_data, dict):
                        parser.add_section(section_name)
                        for key, value in section_data.items():
                            # Convert complex values to JSON strings
                            if isinstance(value, (dict, list)):
                                str_value = json.dumps(value)
                            else:
                                str_value = str(value)
                            parser.set(section_name, key, str_value)
                
                with open(self.ini_config_file, 'w', encoding='utf-8') as f:
                    parser.write(f)
            
            else:
                raise ConfigError(f"Unsupported format: {format}")
            
            self.logger.info(f"Configuration saved in {format} format")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def create_config_template(self, template_path: Optional[Path] = None) -> bool:
        """
        Create a configuration template file.
        
        Args:
            template_path: Path for template file
            
        Returns:
            True if successful
        """
        try:
            if not template_path:
                template_path = self.config_dir / 'config_template.json'
            
            # Create template with comments and examples
            template = {
                "_comment": "Spanish Conjugation GUI Configuration Template",
                "_instructions": {
                    "1": "Copy this file to api_config.json to use",
                    "2": "Remove lines starting with _ (comments)",
                    "3": "Set your API key using the setup wizard or store securely",
                    "4": "Customize settings as needed"
                },
                
                "api": {
                    "_comment": "API Configuration",
                    "provider": "openai",
                    "model": "gpt-4o",
                    "max_tokens": 600,
                    "temperature": 0.5,
                    "timeout": 30,
                    "_note": "API key is stored securely, not in this file"
                },
                
                "security": {
                    "_comment": "Security Settings",
                    "store_credentials_securely": True,
                    "validate_api_keys": True,
                    "encrypt_config": False
                },
                
                "features": {
                    "_comment": "Application Features",
                    "offline_mode": True,
                    "dark_mode": False,
                    "show_translation": False,
                    "exercise_count": 5,
                    "answer_strictness": "normal"
                },
                
                "app": {
                    "_comment": "Application Settings",
                    "debug_mode": False,
                    "log_level": "INFO",
                    "auto_update": True
                }
            }
            
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration template created: {template_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating config template: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration."""
        return {
            "api_provider": self.get('api.provider'),
            "api_model": self.get('api.model'),
            "has_api_key": bool(self.get_api_key()),
            "security_enabled": self.get('security.store_credentials_securely'),
            "offline_mode": self.get('features.offline_mode'),
            "config_files": {
                "json_exists": self.json_config_file.exists(),
                "ini_exists": self.ini_config_file.exists(),
                "user_exists": self.user_config_file.exists()
            },
            "storage_info": self.credentials_manager.get_storage_info(),
            "last_updated": self.get('metadata.last_updated')
        }
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults."""
        try:
            self.config = self._get_default_config()
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Error resetting config: {e}")
            return False