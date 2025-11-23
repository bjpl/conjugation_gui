#!/usr/bin/env python3
"""
Security System Usage Examples for Spanish Conjugation GUI
==========================================================

This file demonstrates how to use the secure API key management system
programmatically. These examples show various use cases and integration patterns.

Author: Brand
Version: 1.0.0
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.security import (
        CredentialsManager, APIConfig, SetupWizard,
        run_setup_wizard, check_first_run
    )
    print("✅ Security modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import security modules: {e}")
    print("Make sure you've installed the required dependencies:")
    print("pip install keyring cryptography aiohttp")
    sys.exit(1)


def example_basic_usage():
    """Demonstrate basic API key management."""
    print("\n🔧 Basic API Key Management")
    print("=" * 40)
    
    # Initialize credentials manager
    manager = CredentialsManager()
    
    # Check available storage methods
    storage_info = manager.get_storage_info()
    print(f"Keyring available: {storage_info['keyring_available']}")
    print(f"Encryption available: {storage_info['encryption_available']}")
    print(f"Supported methods: {storage_info['supported_methods']}")
    
    # Example API key (DO NOT use real keys in examples!)
    test_key = "sk-test_example_key_do_not_use_in_production_12345678901234567890"
    
    # Store API key
    print(f"\n📥 Storing test API key...")
    success = manager.store_credential("openai_api_key", test_key)
    print(f"Storage result: {'✅ Success' if success else '❌ Failed'}")
    
    # Retrieve API key
    print(f"\n📤 Retrieving API key...")
    retrieved_key = manager.retrieve_credential("openai_api_key")
    if retrieved_key:
        # Show partial key for security
        masked_key = retrieved_key[:6] + "*" * (len(retrieved_key) - 10) + retrieved_key[-4:]
        print(f"Retrieved key: {masked_key}")
    else:
        print("❌ No key found")
    
    # Validate API key format
    print(f"\n🔍 Validating API key...")
    validation = manager.validate_credential("openai_api_key", test_key)
    print(f"Valid: {validation['valid']}")
    if validation['errors']:
        print(f"Errors: {validation['errors']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")
    
    # List stored credentials
    print(f"\n📋 Listing stored credentials...")
    credentials = manager.list_credentials()
    print(f"Found credentials: {credentials}")
    
    # Clean up test credential
    print(f"\n🧹 Cleaning up test credential...")
    deleted = manager.delete_credential("openai_api_key")
    print(f"Deletion result: {'✅ Success' if deleted else '❌ Failed'}")


def example_api_config():
    """Demonstrate API configuration management."""
    print("\n⚙️ API Configuration Management")
    print("=" * 40)
    
    # Initialize API configuration
    config = APIConfig()
    
    # Get configuration summary
    summary = config.get_config_summary()
    print(f"API Provider: {summary['api_provider']}")
    print(f"API Model: {summary['api_model']}")
    print(f"Has API Key: {summary['has_api_key']}")
    print(f"Security Enabled: {summary['security_enabled']}")
    print(f"Offline Mode: {summary['offline_mode']}")
    
    # Configuration examples
    print(f"\n📝 Configuration Examples:")
    
    # Get specific values
    model = config.get('api.model', 'gpt-3.5-turbo')
    max_tokens = config.get('api.max_tokens', 500)
    temperature = config.get('api.temperature', 0.7)
    
    print(f"Current model: {model}")
    print(f"Max tokens: {max_tokens}")
    print(f"Temperature: {temperature}")
    
    # Set configuration values
    print(f"\n⚙️ Updating configuration...")
    config.set('api.model', 'gpt-4o')
    config.set('features.offline_mode', False)
    config.set('security.validate_api_keys', True)
    
    # Save configuration
    success = config.save_config('json')
    print(f"Configuration saved: {'✅ Success' if success else '❌ Failed'}")
    
    # Create configuration template
    print(f"\n📋 Creating configuration template...")
    template_created = config.create_config_template()
    print(f"Template created: {'✅ Success' if template_created else '❌ Failed'}")


def example_environment_management():
    """Demonstrate environment variable management."""
    print("\n🌍 Environment Variable Management")
    print("=" * 40)
    
    from src.security.env_manager import EnvironmentManager
    
    # Initialize environment manager
    env_manager = EnvironmentManager()
    
    # Validate current environment
    validation = env_manager.validate_env_setup()
    print(f"Environment status: {validation['status']}")
    print(f"Environment files found: {validation['env_files_found']}")
    print(f"Dotenv available: {validation['dotenv_available']}")
    
    if validation['issues']:
        print(f"Issues found: {validation['issues']}")
    
    if validation['recommendations']:
        print(f"Recommendations: {validation['recommendations']}")
    
    # Check for API keys in environment
    print(f"\n🔑 API Key Detection:")
    for provider, info in validation['api_keys_found'].items():
        status = "✅ Found" if info['found'] else "❌ Not found"
        print(f"{provider.capitalize()}: {status}")
        if info['found']:
            print(f"  Length: {info['length']} chars")
            print(f"  Prefix: {info['prefix']}")
    
    # Get environment variables with fallback patterns
    print(f"\n📥 Environment Variable Retrieval:")
    api_key = env_manager.get_env_var('API_KEY', default='not_found')
    debug_mode = env_manager.get_env_var('DEBUG', default=False, var_type=bool)
    max_tokens = env_manager.get_env_var('MAX_TOKENS', default=600, var_type=int)
    
    print(f"API Key: {'Found' if api_key != 'not_found' else 'Not found'}")
    print(f"Debug mode: {debug_mode}")
    print(f"Max tokens: {max_tokens}")
    
    # Create environment template
    print(f"\n📋 Creating environment template...")
    try:
        template_path = env_manager.create_env_template()
        print(f"Template created: {template_path}")
    except Exception as e:
        print(f"❌ Template creation failed: {e}")


def example_validation_system():
    """Demonstrate the validation system."""
    print("\n🔍 API Key Validation System")
    print("=" * 40)
    
    from src.security.validator import APIKeyValidator, ValidationLevel, APIProvider
    
    # Initialize validator
    validator = APIKeyValidator()
    
    # Test keys (these are fake examples)
    test_keys = [
        ("sk-test123456789012345678901234567890123456789012345", APIProvider.OPENAI),
        ("invalid-key", None),
        ("sk-ant-test123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456", APIProvider.ANTHROPIC),
        ("AIzaTest12345678901234567890123456789012345", APIProvider.GOOGLE),
    ]
    
    print(f"🧪 Testing {len(test_keys)} API keys:")
    
    for i, (test_key, expected_provider) in enumerate(test_keys, 1):
        print(f"\nTest {i}: {test_key[:10]}...")
        
        # Auto-detect provider
        detected_provider = validator.detect_provider(test_key)
        print(f"Expected: {expected_provider}")
        print(f"Detected: {detected_provider}")
        
        if detected_provider:
            # Validate with basic level
            result = validator.validate_key_sync(
                test_key, 
                detected_provider, 
                ValidationLevel.BASIC
            )
            
            print(f"Status: {result.status.value}")
            if result.errors:
                print(f"Errors: {result.errors}")
            if result.warnings:
                print(f"Warnings: {result.warnings}")
            if result.security_issues:
                print(f"Security issues: {result.security_issues}")
    
    # Create validation report
    print(f"\n📊 Validation Report:")
    # This would normally be done with real results
    print("Report generation would include:")
    print("- Total keys validated")
    print("- Success/failure rates")
    print("- Common issues found")
    print("- Security recommendations")


def example_backup_system():
    """Demonstrate the backup system."""
    print("\n💾 Backup System")
    print("=" * 40)
    
    from src.security.backup_manager import BackupManager
    
    # Initialize backup manager
    backup_manager = BackupManager()
    
    # Get backup status
    status = backup_manager.get_backup_status()
    print(f"Backup directory: {status['backup_dir']}")
    print(f"Total backups: {status['total_backups']}")
    print(f"Encryption enabled: {status['settings']['encryption_enabled']}")
    print(f"Compression enabled: {status['settings']['compression_enabled']}")
    
    # List existing backups
    backups = backup_manager.list_backups()
    print(f"\n📋 Existing backups: {len(backups)}")
    
    for backup in backups[:3]:  # Show first 3
        print(f"  - {backup['name']} ({backup.get('backup_type', 'unknown')})")
        print(f"    Size: {backup['size']:,} bytes")
        print(f"    Created: {backup['created']}")
    
    # Create a test backup (minimal to avoid creating large files)
    print(f"\n📦 Creating test backup...")
    try:
        result = backup_manager.create_backup(
            backup_type='minimal',
            encrypt=False  # Skip encryption for example
        )
        
        if result['success']:
            print(f"✅ Backup created: {result['backup_file']}")
            print(f"Files backed up: {result['metadata']['files_count']}")
        else:
            print(f"❌ Backup failed: {result['error']}")
    
    except Exception as e:
        print(f"❌ Backup example failed: {e}")
        print("This is normal if the application hasn't been set up yet")


def example_first_run_detection():
    """Demonstrate first-run detection and setup."""
    print("\n🚀 First-Run Detection")
    print("=" * 40)
    
    # Check if this is a first run
    is_first_run = check_first_run()
    print(f"Is first run: {is_first_run}")
    
    if is_first_run:
        print("📝 This appears to be a first run!")
        print("In a real application, this would:")
        print("- Show the setup wizard")
        print("- Guide the user through API key configuration")
        print("- Set up security preferences")
        print("- Create initial configuration files")
        
        # Note: We don't actually run the setup wizard in this example
        # because it requires a GUI environment
        print("\n⚠️ Setup wizard not run in this example (requires GUI)")
    else:
        print("✅ Application has been set up previously")
        print("Configuration files exist and setup is complete")


def example_integration_patterns():
    """Show common integration patterns."""
    print("\n🔧 Integration Patterns")
    print("=" * 40)
    
    print("1. Simple API Key Retrieval:")
    print("```python")
    print("from src.security import APIConfig")
    print("config = APIConfig()")
    print("api_key = config.get_api_key()")
    print("```")
    
    print("\n2. Secure Storage with Validation:")
    print("```python")
    print("from src.security import CredentialsManager")
    print("manager = CredentialsManager()")
    print("if manager.validate_credential('openai_api_key', key)['valid']:")
    print("    manager.store_credential('openai_api_key', key)")
    print("```")
    
    print("\n3. First-Run Setup in GUI Application:")
    print("```python")
    print("from src.security import check_first_run, run_setup_wizard")
    print("if check_first_run():")
    print("    run_setup_wizard(parent_widget)")
    print("```")
    
    print("\n4. Configuration with Fallbacks:")
    print("```python")
    print("from src.security import APIConfig")
    print("config = APIConfig()")
    print("model = config.get('api.model', 'gpt-3.5-turbo')  # with fallback")
    print("```")
    
    print("\n5. Environment Variable Management:")
    print("```python")
    print("from src.security.env_manager import EnvironmentManager")
    print("env = EnvironmentManager()")
    print("api_key = env.get_api_key('openai')")
    print("```")


def main():
    """Run all examples."""
    print("🔐 Spanish Conjugation GUI - Security System Examples")
    print("=" * 60)
    
    try:
        # Run all examples
        example_basic_usage()
        example_api_config()
        example_environment_management()
        example_validation_system()
        example_backup_system()
        example_first_run_detection()
        example_integration_patterns()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("\n📚 For more information, see:")
        print("- docs/SECURITY_SETUP.md")
        print("- docs/API_KEY_SETUP.md")
        
    except Exception as e:
        print(f"\n❌ Example failed with error: {e}")
        print("\nThis might be because:")
        print("- Required dependencies are not installed")
        print("- System keyring is not available")
        print("- Configuration files don't exist yet")
        print("\nTry running the main application first to complete setup.")


if __name__ == "__main__":
    main()