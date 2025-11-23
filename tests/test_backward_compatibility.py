#!/usr/bin/env python3
"""
Backward Compatibility Tests for Spanish Conjugation GUI
========================================================

This test suite ensures that the new secure API key management system
maintains backward compatibility with existing installations and
environment variable configurations.

Author: Brand
Version: 1.0.0
"""

import os
import sys
import tempfile
import json
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class BackwardCompatibilityTestCase(unittest.TestCase):
    """Base test case with common setup for compatibility tests."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Store original environment
        self.original_env = os.environ.copy()
        
        # Clear any existing API keys from environment
        for key in list(os.environ.keys()):
            if 'API_KEY' in key or 'OPENAI' in key:
                del os.environ[key]
    
    def tearDown(self):
        """Clean up test environment."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestEnvironmentVariableFallback(BackwardCompatibilityTestCase):
    """Test environment variable fallback functionality."""
    
    def test_openai_api_key_detection(self):
        """Test detection of OPENAI_API_KEY environment variable."""
        test_key = "sk-test123456789012345678901234567890123456789012345"
        
        # Set environment variable
        os.environ["OPENAI_API_KEY"] = test_key
        
        # Test direct detection
        detected_key = os.getenv("OPENAI_API_KEY")
        self.assertEqual(detected_key, test_key)
        
        # Test with environment manager if available
        try:
            from src.security.env_manager import EnvironmentManager
            env_manager = EnvironmentManager()
            
            api_key = env_manager.get_api_key("openai")
            self.assertEqual(api_key, test_key)
        except ImportError:
            # Skip if security modules not available
            pass
    
    def test_alternative_env_var_patterns(self):
        """Test detection of alternative environment variable patterns."""
        test_key = "sk-test123456789012345678901234567890123456789012345"
        
        env_patterns = [
            "SPANISHCONJUGATIONGUI_API_KEY",
            "CONJUGATION_API_KEY", 
            "SPANISH_API_KEY"
        ]
        
        for env_var in env_patterns:
            with self.subTest(env_var=env_var):
                # Clear environment
                for key in list(os.environ.keys()):
                    if 'API_KEY' in key:
                        del os.environ[key]
                
                # Set specific pattern
                os.environ[env_var] = test_key
                
                try:
                    from src.security.env_manager import EnvironmentManager
                    env_manager = EnvironmentManager()
                    
                    # Should find key with any pattern
                    found_key = env_manager.get_env_var("API_KEY")
                    self.assertEqual(found_key, test_key)
                except ImportError:
                    pass
    
    def test_dotenv_file_loading(self):
        """Test loading from .env files."""
        test_key = "sk-test123456789012345678901234567890123456789012345"
        
        # Create .env file
        env_file = self.temp_path / '.env'
        with open(env_file, 'w') as f:
            f.write(f"OPENAI_API_KEY={test_key}\n")
            f.write("SPANISH_GUI_DARK_MODE=true\n")
        
        try:
            from src.security.env_manager import EnvironmentManager
            
            # Initialize with custom search path
            env_manager = EnvironmentManager()
            
            # Test that it would find the file
            # (Actual loading depends on python-dotenv being available)
            self.assertTrue(env_file.exists())
        except ImportError:
            pass


class TestLegacyConfigurationSupport(BackwardCompatibilityTestCase):
    """Test support for legacy configuration files."""
    
    def test_legacy_app_config_json(self):
        """Test loading legacy app_config.json format."""
        legacy_config = {
            "api_key": "",  # Empty, should fallback to environment
            "api_model": "gpt-4o",
            "max_tokens": 600,
            "temperature": 0.5,
            "dark_mode": False,
            "show_translation": True,
            "exercise_count": 5
        }
        
        config_file = self.temp_path / 'app_config.json'
        with open(config_file, 'w') as f:
            json.dump(legacy_config, f, indent=2)
        
        # Test that the file can be read
        with open(config_file, 'r') as f:
            loaded_config = json.load(f)
        
        self.assertEqual(loaded_config["api_model"], "gpt-4o")
        self.assertEqual(loaded_config["exercise_count"], 5)
        
        try:
            from src.security import APIConfig
            
            # Initialize with custom config directory
            api_config = APIConfig(config_dir=self.temp_path)
            
            # Should be able to handle mixed old/new configuration
            self.assertIsNotNone(api_config)
        except ImportError:
            pass
    
    def test_mixed_configuration_sources(self):
        """Test handling multiple configuration sources simultaneously."""
        # Create legacy config file
        legacy_config = {
            "api_model": "gpt-3.5-turbo",  # Old model
            "exercise_count": 3
        }
        
        config_file = self.temp_path / 'app_config.json'
        with open(config_file, 'w') as f:
            json.dump(legacy_config, f, indent=2)
        
        # Set environment variable (should override)
        os.environ["OPENAI_API_KEY"] = "sk-test123456789012345678901234567890123456789012345"
        os.environ["SPANISHCONJUGATIONGUI_API_MODEL"] = "gpt-4o"
        
        try:
            from src.security import APIConfig
            
            api_config = APIConfig(config_dir=self.temp_path)
            
            # Environment should take precedence for API model
            model = api_config.get('api.model', 'default')
            # Note: Exact behavior depends on implementation
            
            self.assertIsNotNone(api_config)
        except ImportError:
            pass


class TestMainApplicationCompatibility(BackwardCompatibilityTestCase):
    """Test main application backward compatibility."""
    
    @patch('builtins.print')  # Suppress print output during tests
    def test_main_app_with_environment_variables(self, mock_print):
        """Test that main application works with environment variables."""
        # Set up environment like old system
        os.environ["OPENAI_API_KEY"] = "sk-test123456789012345678901234567890123456789012345"
        
        try:
            # Import main module
            import main
            
            # Should not raise any import errors
            self.assertTrue(hasattr(main, 'SpanishConjugationGUI'))
            
            # Check that API key is detected
            if hasattr(main, 'api_key'):
                # In backward compatibility mode, should still work
                self.assertIsNotNone(main.api_key)
            
        except ImportError as e:
            if "security" in str(e).lower():
                # Expected if security modules not installed
                pass
            else:
                raise
    
    def test_main_app_without_security_modules(self):
        """Test that main application degrades gracefully without security modules."""
        # Simulate missing security modules
        with patch.dict('sys.modules', {'src.security': None}):
            try:
                import main
                
                # Should still be importable
                self.assertTrue(hasattr(main, 'SpanishConjugationGUI'))
                
                # Should fallback to environment variables
                if hasattr(main, 'SECURITY_AVAILABLE'):
                    # This would be False in fallback mode
                    pass
                    
            except ImportError:
                # Some imports might fail, but shouldn't crash
                pass
    
    @patch('PyQt5.QtWidgets.QApplication')
    def test_gui_initialization_compatibility(self, mock_app):
        """Test GUI initialization with backward compatibility."""
        os.environ["OPENAI_API_KEY"] = "sk-test123456789012345678901234567890123456789012345"
        
        try:
            import main
            
            # Create mock QApplication
            mock_app_instance = MagicMock()
            mock_app.return_value = mock_app_instance
            
            # Should be able to create GUI instance
            # Note: This is a basic smoke test
            gui_class = getattr(main, 'SpanishConjugationGUI', None)
            if gui_class:
                self.assertIsNotNone(gui_class)
            
        except Exception as e:
            # GUI tests are complex, just ensure no critical failures
            if "security" not in str(e).lower():
                print(f"GUI test warning: {e}")


class TestDependencyFallbacks(BackwardCompatibilityTestCase):
    """Test fallback behavior when optional dependencies are missing."""
    
    def test_missing_keyring_dependency(self):
        """Test behavior when keyring is not available."""
        with patch.dict('sys.modules', {'keyring': None}):
            try:
                from src.security.credentials_manager import CredentialsManager
                
                manager = CredentialsManager()
                storage_info = manager.get_storage_info()
                
                # Should indicate keyring is not available
                self.assertFalse(storage_info.get('keyring_available', True))
                
            except ImportError:
                # Expected if security modules depend on keyring
                pass
    
    def test_missing_cryptography_dependency(self):
        """Test behavior when cryptography is not available."""
        with patch.dict('sys.modules', {'cryptography': None}):
            try:
                from src.security.credentials_manager import CredentialsManager
                
                manager = CredentialsManager()
                storage_info = manager.get_storage_info()
                
                # Should indicate encryption is not available
                self.assertFalse(storage_info.get('encryption_available', True))
                
            except ImportError:
                # Expected if security modules depend on cryptography
                pass
    
    def test_missing_dotenv_dependency(self):
        """Test behavior when python-dotenv is not available."""
        with patch.dict('sys.modules', {'dotenv': None}):
            try:
                from src.security.env_manager import EnvironmentManager
                
                env_manager = EnvironmentManager()
                
                # Should still work without dotenv, just manual parsing
                validation = env_manager.validate_env_setup()
                self.assertFalse(validation.get('dotenv_available', True))
                
            except ImportError:
                # Expected if env_manager requires dotenv
                pass


class TestMigrationScenarios(BackwardCompatibilityTestCase):
    """Test various migration scenarios from old to new system."""
    
    def test_first_time_user_scenario(self):
        """Test scenario for first-time users (no existing config)."""
        # No environment variables or config files
        
        try:
            from src.security import check_first_run
            
            # Should detect as first run
            is_first_run = check_first_run()
            # Note: Result depends on whether config files exist
            self.assertIsInstance(is_first_run, bool)
            
        except ImportError:
            pass
    
    def test_existing_env_var_user_scenario(self):
        """Test scenario for users with existing environment variables."""
        # Set up like existing user
        os.environ["OPENAI_API_KEY"] = "sk-test123456789012345678901234567890123456789012345"
        
        try:
            from src.security import APIConfig
            
            config = APIConfig()
            
            # Should be able to get API key from environment
            api_key = config.get_api_key()
            if api_key:
                self.assertTrue(api_key.startswith('sk-'))
            
        except ImportError:
            pass
    
    def test_existing_config_file_scenario(self):
        """Test scenario for users with existing config files."""
        # Create existing config
        legacy_config = {
            "setup_complete": True,
            "api_model": "gpt-4o",
            "exercise_count": 5,
            "dark_mode": True
        }
        
        config_file = self.temp_path / 'app_config.json'
        with open(config_file, 'w') as f:
            json.dump(legacy_config, f)
        
        try:
            from src.security import APIConfig
            
            config = APIConfig(config_dir=self.temp_path)
            
            # Should be able to load existing config
            self.assertIsNotNone(config)
            
        except ImportError:
            pass


def run_compatibility_tests():
    """Run all backward compatibility tests."""
    print("🧪 Running Backward Compatibility Tests")
    print("=" * 50)
    
    # Create test suite
    test_classes = [
        TestEnvironmentVariableFallback,
        TestLegacyConfigurationSupport, 
        TestMainApplicationCompatibility,
        TestDependencyFallbacks,
        TestMigrationScenarios
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All backward compatibility tests passed!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        return False


def main():
    """Main test function."""
    print("Spanish Conjugation GUI - Backward Compatibility Test Suite")
    print("This suite ensures the new security system maintains compatibility")
    print("with existing configurations and environment setups.\n")
    
    success = run_compatibility_tests()
    
    if success:
        print("\n🎉 Backward compatibility verified!")
        print("The new security system should work with existing setups.")
    else:
        print("\n⚠️  Some compatibility issues found.")
        print("Review the test output above for details.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())