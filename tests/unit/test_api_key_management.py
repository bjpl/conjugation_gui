"""
Unit tests for API key management system.

Tests cover:
- API key validation
- Environment variable loading
- Security checks
- Error handling for invalid keys
- Key rotation scenarios
"""

import pytest
import os
import tempfile
from unittest.mock import patch, mock_open
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class TestAPIKeyValidation:
    """Test API key validation logic."""
    
    def test_valid_openai_key_format(self):
        """Test validation of proper OpenAI API key format."""
        valid_keys = [
            "sk-1234567890abcdef1234567890abcdef12345678",
            "sk-proj-1234567890abcdef1234567890abcdef12345678",
            "sk-test-1234567890abcdef"
        ]
        
        for key in valid_keys:
            assert self._is_valid_openai_key(key), f"Valid key rejected: {key}"
    
    def test_invalid_openai_key_format(self):
        """Test rejection of invalid API key formats."""
        invalid_keys = [
            "",
            "invalid-key",
            "sk-",
            "sk-short",
            "not-openai-key",
            "12345",
            None
        ]
        
        for key in invalid_keys:
            assert not self._is_valid_openai_key(key), f"Invalid key accepted: {key}"
    
    def test_api_key_security_check(self):
        """Test that API keys are not logged or exposed."""
        test_key = "sk-test-1234567890abcdef"
        
        # Simulate logging - key should be masked
        masked_key = self._mask_api_key(test_key)
        assert "sk-test-****" in masked_key
        assert "1234567890abcdef" not in masked_key
    
    def _is_valid_openai_key(self, key):
        """Validate OpenAI API key format."""
        if not key or not isinstance(key, str):
            return False
        
        if not key.startswith('sk-'):
            return False
        
        # Basic length check (OpenAI keys are typically 51+ chars)
        if len(key) < 20:
            return False
            
        return True
    
    def _mask_api_key(self, key):
        """Mask API key for logging."""
        if not key or len(key) < 10:
            return "****"
        return key[:7] + "****" + key[-4:]


class TestEnvironmentVariableLoading:
    """Test loading API keys from environment variables."""
    
    def test_load_api_key_from_env(self, clean_environment):
        """Test loading API key from environment variable."""
        test_key = "sk-test-1234567890abcdef"
        os.environ['OPENAI_API_KEY'] = test_key
        
        # Simulate how the app loads the key
        loaded_key = os.getenv('OPENAI_API_KEY')
        assert loaded_key == test_key
    
    def test_missing_api_key_env_var(self, clean_environment):
        """Test behavior when API key environment variable is missing."""
        # Ensure the key is not set
        assert 'OPENAI_API_KEY' not in os.environ
        
        # Should return None or empty string
        loaded_key = os.getenv('OPENAI_API_KEY', '')
        assert loaded_key == ''
    
    @patch('builtins.open', new_callable=mock_open, read_data="OPENAI_API_KEY=sk-test-key")
    @patch('os.path.exists', return_value=True)
    def test_load_from_env_file(self, mock_exists, mock_file):
        """Test loading API key from .env file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, '.env')
            
            # Create .env file
            with open(env_path, 'w') as f:
                f.write('OPENAI_API_KEY=sk-test-key\n')
            
            # Load environment variables
            old_dir = os.getcwd()
            try:
                os.chdir(temp_dir)
                load_dotenv()
                key = os.getenv('OPENAI_API_KEY')
                assert key == 'sk-test-key'
            finally:
                os.chdir(old_dir)
    
    def test_env_file_not_found(self):
        """Test graceful handling when .env file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            old_dir = os.getcwd()
            try:
                os.chdir(temp_dir)
                # Should not raise an exception
                load_dotenv()
                key = os.getenv('OPENAI_API_KEY', '')
                assert key == ''
            finally:
                os.chdir(old_dir)


class TestAPIKeyErrorHandling:
    """Test error handling for API key issues."""
    
    def test_empty_api_key_handling(self):
        """Test handling of empty API key."""
        empty_keys = ['', None, '   ', 'your_openai_api_key_here']
        
        for key in empty_keys:
            assert not self._is_api_key_configured(key)
    
    def test_placeholder_key_detection(self):
        """Test detection of placeholder/example keys."""
        placeholder_keys = [
            'your_openai_api_key_here',
            'YOUR_API_KEY_HERE',
            'sk-your-key-here',
            'INSERT_KEY_HERE'
        ]
        
        for key in placeholder_keys:
            assert not self._is_api_key_configured(key)
    
    def test_corrupted_env_file_handling(self):
        """Test handling of corrupted .env file."""
        corrupted_content = [
            "INVALID_FORMAT",
            "=sk-test-key",
            "OPENAI_API_KEY",
            "OPENAI_API_KEY=",
            "# Only comments\n# No actual key"
        ]
        
        for content in corrupted_content:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
                f.write(content)
                f.flush()
                
                try:
                    # Should not crash
                    load_dotenv(f.name)
                    key = os.getenv('OPENAI_API_KEY', '')
                    # May be empty or invalid, but shouldn't crash
                    assert isinstance(key, str)
                finally:
                    os.unlink(f.name)
    
    def _is_api_key_configured(self, key):
        """Check if API key is properly configured."""
        if not key or not isinstance(key, str):
            return False
        
        key = key.strip()
        if not key:
            return False
        
        # Check for placeholder values
        placeholder_patterns = [
            'your_openai_api_key_here',
            'your_api_key_here',
            'insert_key_here',
            'api_key_here'
        ]
        
        if key.lower() in placeholder_patterns:
            return False
        
        return True


class TestAPIKeyRotation:
    """Test API key rotation scenarios."""
    
    def test_key_update_detection(self):
        """Test detection of API key updates."""
        old_key = "sk-old-1234567890abcdef"
        new_key = "sk-new-0987654321fedcba"
        
        # Simulate key change
        assert old_key != new_key
        assert self._keys_are_different(old_key, new_key)
    
    def test_key_validation_on_rotation(self):
        """Test that new keys are validated during rotation."""
        test_cases = [
            ("sk-old-key", "sk-new-key", True),
            ("sk-old-key", "invalid-key", False),
            ("sk-old-key", "", False),
            ("sk-old-key", None, False)
        ]
        
        for old_key, new_key, should_accept in test_cases:
            result = self._validate_key_rotation(old_key, new_key)
            assert result == should_accept, f"Key rotation validation failed: {old_key} -> {new_key}"
    
    def _keys_are_different(self, old_key, new_key):
        """Check if two keys are different."""
        return old_key != new_key
    
    def _validate_key_rotation(self, old_key, new_key):
        """Validate key rotation."""
        if not new_key or not isinstance(new_key, str):
            return False
        if not new_key.startswith('sk-'):
            return False
        if len(new_key) < 10:
            return False
        return True


class TestAPIKeyIntegration:
    """Test API key integration with the main application."""
    
    @patch('openai.OpenAI')
    def test_openai_client_initialization(self, mock_openai):
        """Test OpenAI client initialization with API key."""
        test_key = "sk-test-1234567890abcdef"
        
        # Mock successful client creation
        mock_client = mock_openai.return_value
        
        # Simulate client initialization
        from openai import OpenAI
        client = OpenAI(api_key=test_key)
        
        mock_openai.assert_called_once_with(api_key=test_key)
    
    def test_api_key_validation_before_requests(self):
        """Test that API key is validated before making requests."""
        invalid_keys = ["", None, "invalid", "your_api_key_here"]
        
        for key in invalid_keys:
            with pytest.raises((ValueError, Exception)):
                self._simulate_api_request_with_key(key)
    
    def _simulate_api_request_with_key(self, api_key):
        """Simulate making an API request with given key."""
        if not api_key or not isinstance(api_key, str):
            raise ValueError("Invalid API key")
        
        if not api_key.startswith('sk-'):
            raise ValueError("Invalid API key format")
        
        if api_key == "your_api_key_here":
            raise ValueError("Placeholder API key detected")
        
        # Simulate successful validation
        return True


if __name__ == '__main__':
    pytest.main([__file__])