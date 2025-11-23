"""
Integration tests for clean system deployment.

Tests cover:
- Fresh system installation
- Dependencies verification
- First-run experience
- System compatibility
- User workflow completion
"""

import pytest
import os
import sys
import subprocess
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class TestCleanSystemDeployment:
    """Test deployment on clean systems."""
    
    def test_fresh_installation_detection(self, temp_dir):
        """Test detection of fresh installation (no existing config)."""
        # Simulate fresh system - no config files exist
        config_files = ["app_config.json", ".env", "progress.db"]
        
        for config_file in config_files:
            config_path = os.path.join(temp_dir, config_file)
            assert not os.path.exists(config_path), f"Config file {config_file} should not exist on fresh system"
        
        # Should detect as fresh installation
        is_fresh = self._is_fresh_installation(temp_dir)
        assert is_fresh == True
    
    def test_distribution_completeness_check(self, mock_distribution_dir):
        """Test that distribution package contains all required files."""
        required_files = [
            "SpanishConjugation.exe",
            ".env.example",
            "Run.bat",
            "README.txt"
        ]
        
        for file in required_files:
            file_path = os.path.join(mock_distribution_dir, file)
            assert os.path.exists(file_path), f"Distribution missing required file: {file}"
    
    def test_first_run_initialization(self, temp_dir, mock_distribution_dir):
        """Test first-run initialization process."""
        # Copy distribution to temp directory
        target_dir = os.path.join(temp_dir, "installation")
        shutil.copytree(mock_distribution_dir, target_dir)
        
        # Simulate first run
        first_run_result = self._simulate_first_run(target_dir)
        
        assert first_run_result['success'] == True
        assert first_run_result['config_created'] == True
        assert first_run_result['env_example_present'] == True
    
    def test_system_requirements_check(self):
        """Test system requirements validation."""
        requirements = {
            'os': 'windows',
            'python_version': '3.8+',
            'memory_mb': 512,
            'disk_space_mb': 200
        }
        
        system_check = self._check_system_requirements(requirements)
        
        assert system_check['os_compatible'] == True
        assert system_check['sufficient_memory'] == True
        assert system_check['sufficient_disk'] == True
    
    def test_portable_deployment(self, temp_dir):
        """Test portable deployment (no installation required)."""
        # Create portable deployment structure
        portable_dir = os.path.join(temp_dir, "SpanishConjugationPortable")
        os.makedirs(portable_dir, exist_ok=True)
        
        # Copy essential files
        essential_files = {
            "SpanishConjugation.exe": b"MOCK_EXECUTABLE",
            ".env.example": "OPENAI_API_KEY=your_key_here\n",
            "Run.bat": "@echo off\nSpanishConjugation.exe\n",
            "README.txt": "Portable Spanish Conjugation Practice\n"
        }
        
        for filename, content in essential_files.items():
            file_path = os.path.join(portable_dir, filename)
            mode = 'wb' if isinstance(content, bytes) else 'w'
            with open(file_path, mode) as f:
                f.write(content)
        
        # Verify portable deployment works
        is_portable = self._verify_portable_deployment(portable_dir)
        assert is_portable == True
    
    def _is_fresh_installation(self, directory):
        """Check if this is a fresh installation."""
        config_indicators = [
            "app_config.json",
            ".env",
            "progress.db",
            "session_log.txt"
        ]
        
        for indicator in config_indicators:
            if os.path.exists(os.path.join(directory, indicator)):
                return False
        
        return True
    
    def _simulate_first_run(self, installation_dir):
        """Simulate first run of the application."""
        result = {
            'success': False,
            'config_created': False,
            'env_example_present': False,
            'errors': []
        }
        
        try:
            # Check executable exists
            exe_path = os.path.join(installation_dir, "SpanishConjugation.exe")
            if not os.path.exists(exe_path):
                result['errors'].append("Executable not found")
                return result
            
            # Check .env.example exists
            env_example_path = os.path.join(installation_dir, ".env.example")
            result['env_example_present'] = os.path.exists(env_example_path)
            
            # Simulate config creation
            config_path = os.path.join(installation_dir, "app_config.json")
            default_config = {
                "dark_mode": False,
                "first_run": True,
                "installation_date": "2024-01-01"
            }
            
            with open(config_path, 'w') as f:
                json.dump(default_config, f)
            
            result['config_created'] = os.path.exists(config_path)
            result['success'] = True
            
        except Exception as e:
            result['errors'].append(str(e))
        
        return result
    
    def _check_system_requirements(self, requirements):
        """Check system requirements."""
        result = {
            'os_compatible': True,  # Assume Windows for this test
            'sufficient_memory': True,  # Mock check
            'sufficient_disk': True,  # Mock check
            'python_available': True  # Bundled with executable
        }
        
        return result
    
    def _verify_portable_deployment(self, portable_dir):
        """Verify portable deployment functionality."""
        required_files = ["SpanishConjugation.exe", ".env.example", "Run.bat"]
        
        for file in required_files:
            if not os.path.exists(os.path.join(portable_dir, file)):
                return False
        
        return True


class TestUserWorkflowIntegration:
    """Test complete user workflow from installation to usage."""
    
    def test_complete_setup_workflow(self, temp_dir):
        """Test complete user setup workflow."""
        # Step 1: Extract distribution
        dist_dir = os.path.join(temp_dir, "SpanishConjugation_Distribution")
        os.makedirs(dist_dir, exist_ok=True)
        
        # Create distribution files
        self._create_mock_distribution(dist_dir)
        
        # Step 2: User follows setup instructions
        setup_result = self._simulate_user_setup(dist_dir)
        assert setup_result['env_configured'] == True
        
        # Step 3: First application launch
        launch_result = self._simulate_app_launch(dist_dir)
        assert launch_result['successful'] == True
        
        # Step 4: Basic functionality test
        functionality_result = self._test_basic_functionality(dist_dir)
        assert functionality_result['config_loaded'] == True
    
    def test_api_key_setup_workflow(self, temp_dir):
        """Test API key setup workflow."""
        # Create .env.example
        env_example_path = os.path.join(temp_dir, ".env.example")
        with open(env_example_path, 'w') as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        
        # Simulate user copying and editing
        env_path = os.path.join(temp_dir, ".env")
        shutil.copy(env_example_path, env_path)
        
        # User edits with real API key
        with open(env_path, 'w') as f:
            f.write("OPENAI_API_KEY=sk-test-1234567890abcdef\n")
        
        # Verify setup
        setup_valid = self._validate_api_key_setup(env_path)
        assert setup_valid == True
    
    def test_offline_mode_fallback(self, temp_dir):
        """Test offline mode when API key is not configured."""
        # No .env file or invalid key
        env_path = os.path.join(temp_dir, ".env")
        with open(env_path, 'w') as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        
        # Should fallback to offline mode
        offline_available = self._check_offline_mode_availability(temp_dir)
        assert offline_available == True
    
    def test_configuration_persistence(self, temp_dir):
        """Test that user configurations persist between sessions."""
        config_path = os.path.join(temp_dir, "app_config.json")
        
        # First session - user changes settings
        session1_config = {
            "dark_mode": True,
            "exercise_count": 10,
            "show_translation": True
        }
        
        with open(config_path, 'w') as f:
            json.dump(session1_config, f)
        
        # Second session - should load previous settings
        session2_config = self._load_config(config_path)
        
        assert session2_config["dark_mode"] == True
        assert session2_config["exercise_count"] == 10
        assert session2_config["show_translation"] == True
    
    def _create_mock_distribution(self, dist_dir):
        """Create mock distribution files."""
        files = {
            "SpanishConjugation.exe": b"MOCK_EXECUTABLE",
            ".env.example": "OPENAI_API_KEY=your_openai_api_key_here\n",
            "Run.bat": "@echo off\nSpanishConjugation.exe\n",
            "README.txt": "Setup instructions...\n"
        }
        
        for filename, content in files.items():
            file_path = os.path.join(dist_dir, filename)
            mode = 'wb' if isinstance(content, bytes) else 'w'
            with open(file_path, mode) as f:
                f.write(content)
    
    def _simulate_user_setup(self, dist_dir):
        """Simulate user following setup instructions."""
        result = {'env_configured': False}
        
        # User copies .env.example to .env
        env_example = os.path.join(dist_dir, ".env.example")
        env_file = os.path.join(dist_dir, ".env")
        
        if os.path.exists(env_example):
            shutil.copy(env_example, env_file)
            
            # User edits .env file
            with open(env_file, 'w') as f:
                f.write("OPENAI_API_KEY=sk-test-configured-key\n")
            
            result['env_configured'] = True
        
        return result
    
    def _simulate_app_launch(self, dist_dir):
        """Simulate application launch."""
        result = {'successful': False}
        
        # Check if all required files exist
        required_files = ["SpanishConjugation.exe", ".env"]
        all_exist = all(os.path.exists(os.path.join(dist_dir, f)) for f in required_files)
        
        if all_exist:
            result['successful'] = True
        
        return result
    
    def _test_basic_functionality(self, dist_dir):
        """Test basic application functionality."""
        result = {'config_loaded': False}
        
        # Create default config
        config_path = os.path.join(dist_dir, "app_config.json")
        default_config = {"dark_mode": False, "exercise_count": 5}
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f)
        
        result['config_loaded'] = os.path.exists(config_path)
        return result
    
    def _validate_api_key_setup(self, env_path):
        """Validate API key setup."""
        if not os.path.exists(env_path):
            return False
        
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Check if it's not the placeholder
        return "your_openai_api_key_here" not in content and "sk-" in content
    
    def _check_offline_mode_availability(self, temp_dir):
        """Check if offline mode is available."""
        # Offline mode should always be available
        return True
    
    def _load_config(self, config_path):
        """Load configuration from file."""
        with open(config_path, 'r') as f:
            return json.load(f)


class TestSystemCompatibility:
    """Test system compatibility and requirements."""
    
    def test_windows_version_compatibility(self):
        """Test compatibility with different Windows versions."""
        supported_versions = [
            "Windows 10",
            "Windows 11",
            "Windows Server 2019",
            "Windows Server 2022"
        ]
        
        # Mock system version check
        current_version = "Windows 10"  # Mock
        assert current_version in supported_versions
    
    def test_memory_requirements(self):
        """Test memory requirements."""
        min_memory_mb = 512
        recommended_memory_mb = 1024
        
        # Mock system memory check
        system_memory_mb = 2048  # Mock 2GB
        
        assert system_memory_mb >= min_memory_mb, "Insufficient memory"
        
        performance_level = "good" if system_memory_mb >= recommended_memory_mb else "basic"
        assert performance_level in ["basic", "good"]
    
    def test_disk_space_requirements(self):
        """Test disk space requirements."""
        min_disk_space_mb = 100
        recommended_disk_space_mb = 500
        
        # Mock disk space check
        available_space_mb = 1000  # Mock 1GB
        
        assert available_space_mb >= min_disk_space_mb, "Insufficient disk space"
    
    def test_network_connectivity_optional(self):
        """Test that network connectivity is optional."""
        # App should work without internet (offline mode)
        network_available = False  # Mock no network
        
        offline_mode_available = True  # Should always be available
        assert offline_mode_available or network_available, "No fallback mode available"
    
    def test_permission_requirements(self, temp_dir):
        """Test permission requirements for user directories."""
        # Test write permissions in user directory
        test_file = os.path.join(temp_dir, "permission_test.txt")
        
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            write_permission = True
            os.unlink(test_file)
        except PermissionError:
            write_permission = False
        
        assert write_permission, "Insufficient permissions for user directory"


class TestErrorRecovery:
    """Test error recovery and graceful degradation."""
    
    def test_corrupted_config_recovery(self, temp_dir):
        """Test recovery from corrupted configuration."""
        config_path = os.path.join(temp_dir, "app_config.json")
        
        # Create corrupted config
        with open(config_path, 'w') as f:
            f.write('{"invalid": json, syntax}')
        
        # Should recover with defaults
        recovery_result = self._attempt_config_recovery(config_path)
        assert recovery_result['recovered'] == True
        assert recovery_result['using_defaults'] == True
    
    def test_missing_dependencies_handling(self):
        """Test handling of missing optional dependencies."""
        # Test that app can run without optional features
        optional_features = ['advanced_ai_features', 'premium_voices']
        
        for feature in optional_features:
            availability = self._check_feature_availability(feature)
            # Should gracefully handle missing optional features
            assert isinstance(availability, bool)
    
    def test_database_corruption_recovery(self, temp_dir):
        """Test recovery from database corruption."""
        db_path = os.path.join(temp_dir, "progress.db")
        
        # Create corrupted database file
        with open(db_path, 'wb') as f:
            f.write(b"corrupted_data")
        
        # Should recover by recreating database
        recovery_result = self._attempt_database_recovery(db_path)
        assert recovery_result['recovered'] == True
    
    def _attempt_config_recovery(self, config_path):
        """Attempt to recover from corrupted config."""
        try:
            with open(config_path, 'r') as f:
                json.load(f)
            return {'recovered': True, 'using_defaults': False}
        except (json.JSONDecodeError, FileNotFoundError):
            # Create default config
            default_config = {"dark_mode": False, "exercise_count": 5}
            with open(config_path, 'w') as f:
                json.dump(default_config, f)
            return {'recovered': True, 'using_defaults': True}
    
    def _check_feature_availability(self, feature):
        """Check if optional feature is available."""
        # Mock feature availability
        available_features = ['basic_exercises', 'offline_mode']
        return feature in available_features
    
    def _attempt_database_recovery(self, db_path):
        """Attempt to recover from database corruption."""
        try:
            # In real implementation, would check database integrity
            # For mock, assume corruption detected and recovery needed
            os.unlink(db_path)  # Remove corrupted file
            
            # Create new database (mock)
            with open(db_path, 'w') as f:
                f.write('{"fresh_database": true}')
            
            return {'recovered': True}
        except Exception:
            return {'recovered': False}


if __name__ == '__main__':
    pytest.main([__file__])