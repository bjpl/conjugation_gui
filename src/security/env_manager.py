"""
Environment Variable Management for Spanish Conjugation GUI
===========================================================

This module provides comprehensive environment variable management with fallback
support, validation, and secure handling of environment-based configuration.

Features:
- Automatic .env file detection and loading
- Multiple environment variable name patterns
- Type conversion and validation
- Environment variable templates
- Cross-platform path handling
- Security-focused environment management

Author: Brand
Version: 1.0.0
"""

import os
import logging
from typing import Dict, Optional, Any, List, Union, Callable
from pathlib import Path
import json

try:
    from dotenv import load_dotenv, find_dotenv, set_key
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class EnvironmentManager:
    """
    Comprehensive environment variable manager with fallback support.
    
    Provides automatic detection of environment variables using multiple
    naming patterns and supports .env file management.
    """
    
    def __init__(self, app_name: str = "SpanishConjugationGUI"):
        """
        Initialize environment manager.
        
        Args:
            app_name: Application name for environment variable prefixes
        """
        self.app_name = app_name
        self.logger = logging.getLogger(f'{app_name}.env')
        
        # Environment variable prefixes to try
        self.prefixes = [
            f"{app_name.upper()}_",
            f"{app_name.replace('GUI', '').upper()}_",
            "CONJUGATION_",
            "SPANISH_",
            ""  # No prefix (last resort)
        ]
        
        # Load .env files if available
        self.env_files = self._find_env_files()
        self._load_env_files()
        
        self.logger.info(f"Environment manager initialized with {len(self.env_files)} .env files")
    
    def _find_env_files(self) -> List[Path]:
        """Find all relevant .env files."""
        env_files = []
        
        # Common .env file names
        env_names = [
            '.env',
            '.env.local',
            '.env.development',
            '.env.production',
            f'.env.{self.app_name.lower()}',
            'config.env'
        ]
        
        # Search locations
        search_paths = [
            Path.cwd(),  # Current directory
            Path.home(),  # Home directory
            Path.home() / '.config' / self.app_name.lower(),  # User config
        ]
        
        # Add parent directories up to 3 levels
        current = Path.cwd()
        for _ in range(3):
            current = current.parent
            search_paths.append(current)
        
        # Find existing .env files
        for search_path in search_paths:
            if search_path.exists():
                for env_name in env_names:
                    env_path = search_path / env_name
                    if env_path.exists() and env_path not in env_files:
                        env_files.append(env_path)
        
        # Use dotenv to find .env files if available
        if DOTENV_AVAILABLE:
            try:
                dotenv_path = find_dotenv()
                if dotenv_path:
                    dotenv_file = Path(dotenv_path)
                    if dotenv_file not in env_files:
                        env_files.append(dotenv_file)
            except Exception as e:
                self.logger.debug(f"dotenv find_dotenv failed: {e}")
        
        return env_files
    
    def _load_env_files(self) -> None:
        """Load all found .env files."""
        for env_file in self.env_files:
            try:
                if DOTENV_AVAILABLE:
                    load_dotenv(env_file, override=False)
                    self.logger.debug(f"Loaded .env file: {env_file}")
                else:
                    # Manual .env file parsing
                    self._manual_load_env(env_file)
            except Exception as e:
                self.logger.warning(f"Failed to load .env file {env_file}: {e}")
    
    def _manual_load_env(self, env_file: Path) -> None:
        """Manually parse and load .env file."""
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=VALUE format
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # Set environment variable if not already set
                        if key and key not in os.environ:
                            os.environ[key] = value
                    else:
                        self.logger.warning(f"Invalid line in {env_file}:{line_num}: {line}")
                        
        except Exception as e:
            self.logger.error(f"Error manually parsing {env_file}: {e}")
    
    def get_env_var(self, 
                    base_key: str, 
                    default: Any = None,
                    var_type: type = str,
                    required: bool = False) -> Any:
        """
        Get environment variable with multiple name pattern fallback.
        
        Args:
            base_key: Base key name (e.g., 'API_KEY')
            default: Default value if not found
            var_type: Type to convert to (str, int, bool, float, list, dict)
            required: Raise error if not found and no default
            
        Returns:
            Environment variable value converted to specified type
        """
        # Generate possible environment variable names
        possible_names = []
        
        # Add prefixed versions
        for prefix in self.prefixes:
            possible_names.append(f"{prefix}{base_key}")
        
        # Add common alternative patterns
        alt_patterns = [
            base_key.replace('_', ''),  # Remove underscores
            base_key.lower(),  # Lowercase
            base_key.upper(),  # Uppercase (redundant but explicit)
        ]
        
        for pattern in alt_patterns:
            for prefix in self.prefixes:
                name = f"{prefix}{pattern}"
                if name not in possible_names:
                    possible_names.append(name)
        
        # Search for the variable
        raw_value = None
        found_key = None
        
        for name in possible_names:
            if name in os.environ:
                raw_value = os.environ[name]
                found_key = name
                break
        
        if raw_value is None:
            if required and default is None:
                raise ValueError(f"Required environment variable not found. Tried: {possible_names}")
            return default
        
        # Convert to requested type
        try:
            converted_value = self._convert_env_value(raw_value, var_type)
            self.logger.debug(f"Found {found_key}={converted_value} (type: {var_type.__name__})")
            return converted_value
        except (ValueError, TypeError) as e:
            self.logger.error(f"Failed to convert {found_key}={raw_value} to {var_type.__name__}: {e}")
            if required and default is None:
                raise
            return default
    
    def _convert_env_value(self, value: str, var_type: type) -> Any:
        """Convert environment variable string to specified type."""
        if var_type == str:
            return value
        
        elif var_type == bool:
            return value.lower() in ('true', 'yes', '1', 'on', 'enabled')
        
        elif var_type == int:
            return int(value)
        
        elif var_type == float:
            return float(value)
        
        elif var_type == list:
            # Handle comma-separated values or JSON
            if value.strip().startswith('['):
                return json.loads(value)
            else:
                return [item.strip() for item in value.split(',')]
        
        elif var_type == dict:
            return json.loads(value)
        
        else:
            # Try to use the type's constructor
            return var_type(value)
    
    def set_env_var(self, key: str, value: Any, env_file: Optional[Path] = None) -> bool:
        """
        Set environment variable and optionally save to .env file.
        
        Args:
            key: Environment variable name
            value: Value to set
            env_file: Optional .env file to update
            
        Returns:
            True if successful
        """
        try:
            # Convert value to string
            if isinstance(value, bool):
                str_value = 'true' if value else 'false'
            elif isinstance(value, (list, dict)):
                str_value = json.dumps(value)
            else:
                str_value = str(value)
            
            # Set in current environment
            os.environ[key] = str_value
            
            # Save to .env file if specified
            if env_file:
                if DOTENV_AVAILABLE:
                    set_key(str(env_file), key, str_value)
                else:
                    self._manual_set_env(env_file, key, str_value)
            
            self.logger.info(f"Set environment variable: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set environment variable {key}: {e}")
            return False
    
    def _manual_set_env(self, env_file: Path, key: str, value: str) -> None:
        """Manually update .env file."""
        lines = []
        key_found = False
        
        # Read existing file if it exists
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # Update or add the key
        new_lines = []
        for line in lines:
            if line.strip().startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                key_found = True
            else:
                new_lines.append(line)
        
        # Add new key if not found
        if not key_found:
            new_lines.append(f"{key}={value}\n")
        
        # Write back to file
        env_file.parent.mkdir(parents=True, exist_ok=True)
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    
    def get_api_key(self, provider: str = "openai") -> Optional[str]:
        """
        Get API key for specified provider using multiple patterns.
        
        Args:
            provider: API provider name
            
        Returns:
            API key or None if not found
        """
        # Common API key patterns
        key_patterns = [
            f"{provider}_api_key",
            f"{provider}_key",
            "api_key",
            f"{provider}",
            f"{provider}_token",
            "token"
        ]
        
        for pattern in key_patterns:
            api_key = self.get_env_var(pattern.upper())
            if api_key:
                self.logger.debug(f"Found API key for {provider} using pattern: {pattern}")
                return api_key
        
        # Try OpenAI-specific patterns as fallback
        if provider != "openai":
            openai_key = self.get_env_var("OPENAI_API_KEY")
            if openai_key:
                self.logger.debug(f"Using OpenAI key as fallback for {provider}")
                return openai_key
        
        return None
    
    def validate_env_setup(self) -> Dict[str, Any]:
        """
        Validate current environment setup.
        
        Returns:
            Validation report
        """
        report = {
            "status": "ok",
            "env_files_found": len(self.env_files),
            "env_files": [str(f) for f in self.env_files],
            "issues": [],
            "recommendations": [],
            "api_keys_found": {},
            "dotenv_available": DOTENV_AVAILABLE
        }
        
        # Check for API keys
        providers = ["openai", "anthropic", "google"]
        for provider in providers:
            api_key = self.get_api_key(provider)
            if api_key:
                report["api_keys_found"][provider] = {
                    "found": True,
                    "length": len(api_key),
                    "prefix": api_key[:10] + "..." if len(api_key) > 10 else api_key
                }
            else:
                report["api_keys_found"][provider] = {"found": False}
        
        # Check if no API keys found
        if not any(info["found"] for info in report["api_keys_found"].values()):
            report["issues"].append("No API keys found in environment")
            report["recommendations"].append("Set OPENAI_API_KEY or run the setup wizard")
        
        # Check for .env files
        if not self.env_files:
            report["recommendations"].append("Consider creating a .env file for easier configuration")
        
        # Check if dotenv is available
        if not DOTENV_AVAILABLE:
            report["issues"].append("python-dotenv not installed - .env files may not load properly")
            report["recommendations"].append("Install python-dotenv: pip install python-dotenv")
        
        # Set overall status
        if report["issues"]:
            report["status"] = "issues_found"
        elif report["recommendations"]:
            report["status"] = "improvements_available"
        
        return report
    
    def create_env_template(self, template_path: Optional[Path] = None) -> Path:
        """
        Create a .env template file with common variables.
        
        Args:
            template_path: Optional custom template path
            
        Returns:
            Path to created template file
        """
        if not template_path:
            template_path = Path.cwd() / '.env.template'
        
        template_content = f"""# {self.app_name} Environment Configuration Template
# Copy this file to .env and fill in your values

# ============================================
# API Configuration
# ============================================

# OpenAI API Key (required for AI-powered features)
# Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-api-key-here

# Alternative API key names (pick one)
# {self.app_name.upper()}_OPENAI_KEY=sk-your-api-key-here
# CONJUGATION_API_KEY=sk-your-api-key-here

# ============================================
# Application Settings
# ============================================

# Default AI model to use
{self.app_name.upper()}_API_MODEL=gpt-4o

# Maximum tokens per API request
{self.app_name.upper()}_MAX_TOKENS=600

# AI temperature (0.0-1.0, lower = more consistent)
{self.app_name.upper()}_TEMPERATURE=0.5

# ============================================
# Feature Flags
# ============================================

# Enable offline mode
{self.app_name.upper()}_OFFLINE_MODE=true

# Enable dark mode
{self.app_name.upper()}_DARK_MODE=false

# Show English translations
{self.app_name.upper()}_SHOW_TRANSLATION=false

# Default number of exercises per session
{self.app_name.upper()}_EXERCISE_COUNT=5

# ============================================
# Security Settings
# ============================================

# Validate API keys before storing
{self.app_name.upper()}_VALIDATE_KEYS=true

# Enable security audit logging
{self.app_name.upper()}_AUDIT_LOG=true

# ============================================
# Development Settings
# ============================================

# Enable debug mode
{self.app_name.upper()}_DEBUG=false

# Log level (DEBUG, INFO, WARNING, ERROR)
{self.app_name.upper()}_LOG_LEVEL=INFO

# ============================================
# File Paths (optional)
# ============================================

# Custom configuration directory
# {self.app_name.upper()}_CONFIG_DIR=/path/to/config

# Custom data directory
# {self.app_name.upper()}_DATA_DIR=/path/to/data

# ============================================
# Usage Notes
# ============================================
# 
# 1. Remove the .template extension and rename to .env
# 2. Never commit .env files to version control
# 3. Use quotes for values with spaces: KEY="value with spaces"
# 4. Boolean values: true, false, yes, no, 1, 0
# 5. Lists can be comma-separated: KEY=item1,item2,item3
#
# For more information, see the documentation.
"""
        
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            self.logger.info(f"Environment template created: {template_path}")
            return template_path
            
        except Exception as e:
            self.logger.error(f"Failed to create env template: {e}")
            raise
    
    def get_all_app_env_vars(self) -> Dict[str, str]:
        """Get all environment variables related to this application."""
        app_vars = {}
        
        for key, value in os.environ.items():
            # Check if key matches any of our prefixes
            for prefix in self.prefixes:
                if prefix and key.startswith(prefix):
                    app_vars[key] = value
                    break
            
            # Check for common API key patterns
            if any(pattern in key.lower() for pattern in ['api_key', 'openai', 'conjugation', 'spanish']):
                app_vars[key] = value
        
        return app_vars
    
    def export_env_config(self, export_path: Optional[Path] = None) -> Path:
        """
        Export current environment configuration to a file.
        
        Args:
            export_path: Optional export file path
            
        Returns:
            Path to exported file
        """
        if not export_path:
            export_path = Path.cwd() / f'{self.app_name.lower()}_env_export.env'
        
        app_vars = self.get_all_app_env_vars()
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(f"# {self.app_name} Environment Export\n")
                f.write(f"# Generated on: {os.path.basename(__file__)}\n\n")
                
                for key in sorted(app_vars.keys()):
                    value = app_vars[key]
                    # Mask sensitive values
                    if 'key' in key.lower() or 'token' in key.lower() or 'secret' in key.lower():
                        if len(value) > 10:
                            masked_value = value[:6] + '*' * (len(value) - 10) + value[-4:]
                        else:
                            masked_value = '*' * len(value)
                        f.write(f"{key}={masked_value}  # (masked)\n")
                    else:
                        f.write(f"{key}={value}\n")
            
            self.logger.info(f"Environment config exported to: {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Failed to export env config: {e}")
            raise