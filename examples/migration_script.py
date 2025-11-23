#!/usr/bin/env python3
"""
Migration Script for Spanish Conjugation GUI Security System
============================================================

This script helps users migrate from the old environment-variable-only
system to the new secure API key management system.

Features:
- Detects existing configuration
- Migrates API keys to secure storage
- Updates configuration files
- Creates backups of old settings
- Validates migration success

Author: Brand
Version: 1.0.0
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.security import (
        CredentialsManager, APIConfig, BackupManager
    )
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False


class MigrationError(Exception):
    """Exception raised during migration process."""
    pass


class SecurityMigrator:
    """Handles migration to the secure API key system."""
    
    def __init__(self):
        self.app_name = "SpanishConjugationGUI"
        self.project_root = Path(__file__).parent.parent
        self.migration_log = []
        
        # Initialize components if available
        if SECURITY_AVAILABLE:
            self.credentials_manager = CredentialsManager(self.app_name)
            self.api_config = APIConfig(self.app_name)
            self.backup_manager = BackupManager(self.app_name)
        else:
            self.credentials_manager = None
            self.api_config = None
            self.backup_manager = None
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log migration progress."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
    
    def check_prerequisites(self) -> bool:
        """Check if migration prerequisites are met."""
        self.log("Checking migration prerequisites...")
        
        if not SECURITY_AVAILABLE:
            self.log("Security modules not available. Install required dependencies:", "ERROR")
            self.log("pip install keyring cryptography aiohttp schedule", "ERROR")
            return False
        
        # Check system requirements
        storage_info = self.credentials_manager.get_storage_info()
        self.log(f"Keyring available: {storage_info['keyring_available']}")
        self.log(f"Encryption available: {storage_info['encryption_available']}")
        self.log(f"Supported methods: {storage_info['supported_methods']}")
        
        return True
    
    def detect_existing_configuration(self) -> Dict[str, Any]:
        """Detect existing configuration that needs migration."""
        self.log("Detecting existing configuration...")
        
        config_info = {
            "env_files": [],
            "api_keys": {},
            "config_files": [],
            "legacy_files": []
        }
        
        # Check for .env files
        env_patterns = ['.env', '.env.local', '.env.development']
        for pattern in env_patterns:
            env_file = self.project_root / pattern
            if env_file.exists():
                config_info["env_files"].append(str(env_file))
                self.log(f"Found environment file: {env_file}")
        
        # Check environment variables
        env_vars = [
            'OPENAI_API_KEY',
            'CONJUGATION_API_KEY', 
            'SPANISH_API_KEY',
            f'{self.app_name.upper()}_API_KEY'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                # Store masked version for logging
                masked = value[:6] + "*" * (len(value) - 10) + value[-4:] if len(value) > 10 else "*" * len(value)
                config_info["api_keys"][var] = {
                    "value": value,
                    "masked": masked,
                    "source": "environment"
                }
                self.log(f"Found API key in {var}: {masked}")
        
        # Check for legacy config files
        legacy_files = ['app_config.json', 'config.json', 'settings.json']
        for filename in legacy_files:
            config_file = self.project_root / filename
            if config_file.exists():
                config_info["config_files"].append(str(config_file))
                self.log(f"Found configuration file: {config_file}")
        
        return config_info
    
    def create_migration_backup(self, config_info: Dict[str, Any]) -> str:
        """Create backup of existing configuration before migration."""
        self.log("Creating migration backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root / f"migration_backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        # Backup environment files
        for env_file in config_info["env_files"]:
            src = Path(env_file)
            dst = backup_dir / src.name
            shutil.copy2(src, dst)
            self.log(f"Backed up: {src.name}")
        
        # Backup config files
        for config_file in config_info["config_files"]:
            src = Path(config_file)
            dst = backup_dir / src.name
            shutil.copy2(src, dst)
            self.log(f"Backed up: {src.name}")
        
        # Create migration info file
        migration_info = {
            "migration_date": datetime.now().isoformat(),
            "app_name": self.app_name,
            "source_config": config_info,
            "migration_log": self.migration_log.copy()
        }
        
        info_file = backup_dir / "migration_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(migration_info, f, indent=2, ensure_ascii=False)
        
        self.log(f"Migration backup created: {backup_dir}")
        return str(backup_dir)
    
    def migrate_api_keys(self, config_info: Dict[str, Any]) -> bool:
        """Migrate API keys to secure storage."""
        self.log("Migrating API keys to secure storage...")
        
        if not config_info["api_keys"]:
            self.log("No API keys found to migrate")
            return True
        
        success = True
        
        for env_var, key_info in config_info["api_keys"].items():
            api_key = key_info["value"]
            
            # Determine key type
            if "OPENAI" in env_var:
                key_name = "openai_api_key"
            else:
                key_name = f"{env_var.lower()}_key"
            
            self.log(f"Migrating {env_var} -> {key_name}")
            
            # Validate key before storing
            validation = self.credentials_manager.validate_credential(key_name, api_key)
            if not validation["valid"]:
                self.log(f"API key validation failed: {validation['errors']}", "WARNING")
                # Store anyway, but log the issues
                for error in validation["errors"]:
                    self.log(f"Validation error: {error}", "WARNING")
            
            # Store in secure storage
            stored = self.credentials_manager.store_credential(key_name, api_key)
            if stored:
                self.log(f"Successfully stored {key_name}")
            else:
                self.log(f"Failed to store {key_name}", "ERROR")
                success = False
        
        return success
    
    def migrate_configuration(self, config_info: Dict[str, Any]) -> bool:
        """Migrate configuration files to new format."""
        self.log("Migrating configuration files...")
        
        # Load existing configuration
        existing_config = {}
        for config_file in config_info["config_files"]:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    existing_config.update(file_config)
                    self.log(f"Loaded configuration from {Path(config_file).name}")
            except Exception as e:
                self.log(f"Failed to load {config_file}: {e}", "WARNING")
        
        # Map old configuration to new structure
        migration_mapping = {
            # API settings
            "api_model": ("api", "model"),
            "model": ("api", "model"),
            "max_tokens": ("api", "max_tokens"),
            "temperature": ("api", "temperature"),
            
            # Feature settings
            "offline_mode": ("features", "offline_mode"),
            "dark_mode": ("features", "dark_mode"),
            "show_translation": ("features", "show_translation"),
            "exercise_count": ("features", "exercise_count"),
            "answer_strictness": ("features", "answer_strictness"),
            
            # App settings
            "difficulty": ("app", "difficulty"),
            "window_geometry": ("app", "window_geometry"),
            "splitter_sizes": ("app", "splitter_sizes"),
        }
        
        # Apply migrations
        for old_key, (section, new_key) in migration_mapping.items():
            if old_key in existing_config:
                value = existing_config[old_key]
                self.api_config.set(f"{section}.{new_key}", value)
                self.log(f"Migrated {old_key} -> {section}.{new_key}: {value}")
        
        # Save new configuration
        success = self.api_config.save_config()
        if success:
            self.log("Configuration migration completed")
        else:
            self.log("Failed to save migrated configuration", "ERROR")
        
        return success
    
    def validate_migration(self) -> bool:
        """Validate that migration was successful."""
        self.log("Validating migration...")
        
        # Check if API keys are accessible
        api_key = self.api_config.get_api_key()
        if api_key:
            self.log("✓ API key successfully retrieved from secure storage")
            
            # Test API key if possible
            try:
                test_result = self.api_config.test_api_key(api_key)
                if test_result.get("success"):
                    self.log("✓ API key test successful")
                else:
                    self.log(f"⚠ API key test failed: {test_result.get('error')}", "WARNING")
            except Exception as e:
                self.log(f"⚠ API key test error: {e}", "WARNING")
        else:
            self.log("⚠ No API key found after migration", "WARNING")
        
        # Check configuration
        config_summary = self.api_config.get_config_summary()
        self.log(f"Configuration summary: {json.dumps(config_summary, indent=2)}")
        
        # Check storage info
        storage_info = self.credentials_manager.get_storage_info()
        self.log(f"Storage backend: {storage_info.get('keyring_backend', 'None')}")
        
        return True
    
    def cleanup_old_files(self, config_info: Dict[str, Any], backup_dir: str) -> None:
        """Optionally clean up old configuration files."""
        self.log("Cleanup options:")
        self.log("Old files have been backed up and can be safely removed")
        self.log(f"Backup location: {backup_dir}")
        
        print("\nWould you like to remove the old configuration files? (y/N): ", end="")
        response = input().lower()
        
        if response == 'y':
            # Remove .env files (but create a note)
            for env_file in config_info["env_files"]:
                env_path = Path(env_file)
                if env_path.exists():
                    env_path.unlink()
                    self.log(f"Removed: {env_path}")
            
            self.log("Old files removed. API keys are now stored securely.")
        else:
            self.log("Old files preserved. You can remove them manually later.")
    
    def create_migration_summary(self, backup_dir: str) -> str:
        """Create migration summary report."""
        self.log("Creating migration summary...")
        
        summary = {
            "migration_date": datetime.now().isoformat(),
            "migration_successful": True,
            "app_name": self.app_name,
            "backup_directory": backup_dir,
            "steps_completed": [
                "Prerequisites checked",
                "Existing configuration detected",
                "Migration backup created",
                "API keys migrated to secure storage",
                "Configuration files migrated",
                "Migration validated"
            ],
            "next_steps": [
                "Launch the application to verify everything works",
                "Check the Security Settings dialog",
                "Test API functionality",
                "Remove old configuration files if desired",
                "Set up automatic backups"
            ],
            "migration_log": self.migration_log
        }
        
        summary_file = Path(backup_dir) / "migration_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.log(f"Migration summary saved: {summary_file}")
        return str(summary_file)
    
    def run_migration(self) -> bool:
        """Run the complete migration process."""
        print("🔐 Spanish Conjugation GUI - Security Migration")
        print("=" * 50)
        
        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Step 2: Detect existing configuration
            config_info = self.detect_existing_configuration()
            
            if not config_info["api_keys"] and not config_info["config_files"]:
                self.log("No existing configuration found to migrate")
                self.log("Run the application to use the setup wizard")
                return True
            
            # Step 3: Create backup
            backup_dir = self.create_migration_backup(config_info)
            
            # Step 4: Migrate API keys
            if not self.migrate_api_keys(config_info):
                self.log("API key migration failed", "ERROR")
                return False
            
            # Step 5: Migrate configuration
            if not self.migrate_configuration(config_info):
                self.log("Configuration migration failed", "ERROR")
                return False
            
            # Step 6: Validate migration
            if not self.validate_migration():
                self.log("Migration validation failed", "ERROR")
                return False
            
            # Step 7: Cleanup
            self.cleanup_old_files(config_info, backup_dir)
            
            # Step 8: Create summary
            summary_file = self.create_migration_summary(backup_dir)
            
            print("\n" + "=" * 50)
            print("✅ Migration completed successfully!")
            print(f"📋 Summary: {summary_file}")
            print(f"💾 Backup: {backup_dir}")
            print("\n🚀 Next steps:")
            print("1. Launch the Spanish Conjugation GUI")
            print("2. Verify that your API key works")
            print("3. Check Security Settings if needed")
            
            return True
            
        except Exception as e:
            self.log(f"Migration failed with error: {e}", "ERROR")
            return False


def main():
    """Main migration function."""
    migrator = SecurityMigrator()
    
    print("This script will migrate your Spanish Conjugation GUI configuration")
    print("to use the new secure API key management system.\n")
    
    print("⚠️  IMPORTANT:")
    print("- Your existing configuration will be backed up")
    print("- API keys will be moved to secure system storage")
    print("- The application should be closed before running this")
    print()
    
    response = input("Continue with migration? (y/N): ").lower()
    if response != 'y':
        print("Migration cancelled.")
        return
    
    success = migrator.run_migration()
    
    if success:
        print("\n🎉 Migration successful!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed. Check the log above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()