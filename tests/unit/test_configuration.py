"""
Unit tests for configuration loading and saving functionality.

Tests cover:
- Configuration file loading
- Default configuration handling
- Configuration validation
- Configuration persistence
- Error handling for corrupted configs
"""

import pytest
import os
import json
import tempfile
from unittest.mock import patch, mock_open
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from main import AppConfig


class TestConfigurationLoading:
    """Test configuration file loading."""
    
    def test_load_valid_config_file(self, temp_dir):
        """Test loading a valid configuration file."""
        config_path = os.path.join(temp_dir, "test_config.json")
        test_config = {
            "dark_mode": True,
            "show_translation": True,
            "api_model": "gpt-4o",
            "max_tokens": 800,
            "exercise_count": 10
        }
        
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        app_config = AppConfig(config_path)
        assert app_config.get("dark_mode") == True
        assert app_config.get("show_translation") == True
        assert app_config.get("api_model") == "gpt-4o"
        assert app_config.get("max_tokens") == 800
        assert app_config.get("exercise_count") == 10
    
    def test_load_nonexistent_config_file(self, temp_dir):
        """Test loading when config file doesn't exist - should use defaults."""
        config_path = os.path.join(temp_dir, "nonexistent_config.json")
        
        app_config = AppConfig(config_path)
        
        # Should fall back to defaults
        assert app_config.get("dark_mode") == False
        assert app_config.get("show_translation") == False
        assert app_config.get("api_model") == "gpt-4o"
        assert app_config.get("max_tokens") == 600
        assert app_config.get("exercise_count") == 5
    
    def test_load_corrupted_config_file(self, temp_dir):
        """Test handling of corrupted JSON configuration file."""
        config_path = os.path.join(temp_dir, "corrupted_config.json")
        
        # Write invalid JSON
        with open(config_path, 'w') as f:
            f.write('{"invalid": json, "missing": quote}')
        
        app_config = AppConfig(config_path)
        
        # Should fall back to defaults when JSON is corrupted
        assert app_config.get("dark_mode") == False
        assert app_config.get("exercise_count") == 5
    
    def test_load_partial_config_file(self, temp_dir):
        """Test loading config file with only some values."""
        config_path = os.path.join(temp_dir, "partial_config.json")
        partial_config = {
            "dark_mode": True,
            "exercise_count": 15
            # Missing other values
        }
        
        with open(config_path, 'w') as f:
            json.dump(partial_config, f)
        
        app_config = AppConfig(config_path)
        
        # Should use provided values
        assert app_config.get("dark_mode") == True
        assert app_config.get("exercise_count") == 15
        
        # Should use defaults for missing values
        assert app_config.get("show_translation") == False
        assert app_config.get("api_model") == "gpt-4o"
    
    def test_load_config_with_extra_fields(self, temp_dir):
        """Test loading config file with extra/unknown fields."""
        config_path = os.path.join(temp_dir, "extra_fields_config.json")
        config_with_extras = {
            "dark_mode": True,
            "exercise_count": 7,
            "unknown_field": "unknown_value",
            "extra_setting": 123
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_with_extras, f)
        
        app_config = AppConfig(config_path)
        
        # Should handle known fields
        assert app_config.get("dark_mode") == True
        assert app_config.get("exercise_count") == 7
        
        # Should ignore unknown fields gracefully
        assert app_config.get("unknown_field") is None


class TestConfigurationSaving:
    """Test configuration saving functionality."""
    
    def test_save_config_to_file(self, temp_dir):
        """Test saving configuration to file."""
        config_path = os.path.join(temp_dir, "save_test_config.json")
        
        app_config = AppConfig(config_path)
        app_config.set("dark_mode", True)
        app_config.set("exercise_count", 12)
        
        # Verify file was created and contains correct data
        assert os.path.exists(config_path)
        
        with open(config_path, 'r') as f:
            saved_config = json.load(f)
        
        assert saved_config["dark_mode"] == True
        assert saved_config["exercise_count"] == 12
    
    def test_save_config_overwrites_existing(self, temp_dir):
        """Test that saving config overwrites existing file."""
        config_path = os.path.join(temp_dir, "overwrite_test_config.json")
        
        # Create initial config
        initial_config = {"dark_mode": False, "exercise_count": 5}
        with open(config_path, 'w') as f:
            json.dump(initial_config, f)
        
        # Load and modify config
        app_config = AppConfig(config_path)
        app_config.set("dark_mode", True)
        app_config.set("exercise_count", 20)
        
        # Verify changes were saved
        with open(config_path, 'r') as f:
            saved_config = json.load(f)
        
        assert saved_config["dark_mode"] == True
        assert saved_config["exercise_count"] == 20
    
    def test_save_config_with_unicode(self, temp_dir):
        """Test saving configuration with Unicode characters."""
        config_path = os.path.join(temp_dir, "unicode_config.json")
        
        app_config = AppConfig(config_path)
        app_config.set("theme_context", "español, français, 中文")
        
        # Verify Unicode is properly saved
        with open(config_path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        
        assert saved_config["theme_context"] == "español, français, 中文"
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_save_config_permission_error(self, mock_open, temp_dir):
        """Test handling of permission errors when saving config."""
        config_path = os.path.join(temp_dir, "permission_test.json")
        
        app_config = AppConfig(config_path)
        result = app_config.save_config()
        
        # Should return False on permission error
        assert result == False
    
    @patch('json.dump', side_effect=TypeError("Not JSON serializable"))
    def test_save_config_serialization_error(self, mock_dump, temp_dir):
        """Test handling of JSON serialization errors."""
        config_path = os.path.join(temp_dir, "serialization_test.json")
        
        app_config = AppConfig(config_path)
        app_config.config["invalid_object"] = object()  # Non-serializable
        
        result = app_config.save_config()
        assert result == False


class TestConfigurationValidation:
    """Test configuration validation."""
    
    def test_validate_window_geometry(self, temp_dir):
        """Test validation of window geometry configuration."""
        config_path = os.path.join(temp_dir, "geometry_config.json")
        
        valid_geometries = [
            {"width": 1200, "height": 800, "x": 100, "y": 100},
            {"width": 800, "height": 600, "x": 0, "y": 0},
            {"width": 1920, "height": 1080, "x": 50, "y": 50}
        ]
        
        for geometry in valid_geometries:
            config = {"window_geometry": geometry}
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            app_config = AppConfig(config_path)
            loaded_geometry = app_config.get("window_geometry")
            assert loaded_geometry == geometry
    
    def test_validate_api_model_options(self, temp_dir):
        """Test validation of API model configuration."""
        config_path = os.path.join(temp_dir, "model_config.json")
        
        valid_models = ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]
        
        for model in valid_models:
            config = {"api_model": model}
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            app_config = AppConfig(config_path)
            assert app_config.get("api_model") == model
    
    def test_validate_numeric_ranges(self, temp_dir):
        """Test validation of numeric configuration values."""
        config_path = os.path.join(temp_dir, "numeric_config.json")
        
        # Test valid ranges
        valid_configs = [
            {"max_tokens": 100, "temperature": 0.0, "exercise_count": 1},
            {"max_tokens": 2000, "temperature": 1.0, "exercise_count": 50},
            {"max_tokens": 600, "temperature": 0.5, "exercise_count": 10}
        ]
        
        for config in valid_configs:
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            app_config = AppConfig(config_path)
            for key, value in config.items():
                assert app_config.get(key) == value
    
    def test_validate_boolean_settings(self, temp_dir):
        """Test validation of boolean configuration settings."""
        config_path = os.path.join(temp_dir, "boolean_config.json")
        
        boolean_configs = [
            {"dark_mode": True, "show_translation": False},
            {"dark_mode": False, "show_translation": True},
            {"dark_mode": True, "show_translation": True},
            {"dark_mode": False, "show_translation": False}
        ]
        
        for config in boolean_configs:
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            app_config = AppConfig(config_path)
            for key, value in config.items():
                assert app_config.get(key) == value
                assert isinstance(app_config.get(key), bool)


class TestConfigurationDefaults:
    """Test default configuration values."""
    
    def test_default_values_are_valid(self):
        """Test that all default configuration values are valid."""
        app_config = AppConfig("nonexistent_file.json")
        
        # Test boolean defaults
        assert isinstance(app_config.get("dark_mode"), bool)
        assert isinstance(app_config.get("show_translation"), bool)
        
        # Test string defaults
        assert isinstance(app_config.get("api_model"), str)
        assert len(app_config.get("api_model")) > 0
        
        # Test numeric defaults
        assert isinstance(app_config.get("max_tokens"), int)
        assert app_config.get("max_tokens") > 0
        assert isinstance(app_config.get("temperature"), (int, float))
        assert 0 <= app_config.get("temperature") <= 1
        
        # Test nested defaults
        geometry = app_config.get("window_geometry")
        assert isinstance(geometry, dict)
        assert "width" in geometry and geometry["width"] > 0
        assert "height" in geometry and geometry["height"] > 0
    
    def test_fallback_on_missing_key(self):
        """Test fallback behavior for missing configuration keys."""
        app_config = AppConfig("nonexistent_file.json")
        
        # Should return None for unknown keys with no default
        assert app_config.get("unknown_key") is None
        
        # Should return provided default for unknown keys
        assert app_config.get("unknown_key", "default_value") == "default_value"
    
    def test_config_completeness(self):
        """Test that default configuration contains all expected keys."""
        app_config = AppConfig("nonexistent_file.json")
        
        expected_keys = [
            "dark_mode", "show_translation", "api_model", "max_tokens",
            "temperature", "max_stored_responses", "exercise_count",
            "answer_strictness", "window_geometry", "splitter_sizes"
        ]
        
        for key in expected_keys:
            value = app_config.get(key)
            assert value is not None, f"Missing default value for key: {key}"


class TestConfigurationConcurrency:
    """Test configuration handling under concurrent access."""
    
    def test_multiple_config_instances(self, temp_dir):
        """Test behavior with multiple AppConfig instances."""
        config_path = os.path.join(temp_dir, "multi_instance_config.json")
        
        # Create first instance and set value
        config1 = AppConfig(config_path)
        config1.set("dark_mode", True)
        
        # Create second instance - should load updated value
        config2 = AppConfig(config_path)
        assert config2.get("dark_mode") == True
        
        # Modify with second instance
        config2.set("exercise_count", 25)
        
        # First instance should still have old values until reloaded
        assert config1.get("exercise_count") != 25
        
        # But file should contain new values
        config3 = AppConfig(config_path)
        assert config3.get("exercise_count") == 25
        assert config3.get("dark_mode") == True


if __name__ == '__main__':
    pytest.main([__file__])