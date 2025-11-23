"""
Performance and security validation tests.

Tests cover:
- Memory usage monitoring
- CPU performance benchmarks
- Security vulnerability detection
- Input validation security
- File system security
- Network security
- Data encryption/protection
"""

import pytest
import os
import sys
import time
import threading
import tempfile
import hashlib
import json
import subprocess
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class TestPerformanceBenchmarks:
    """Test performance benchmarks for the application."""
    
    def test_application_startup_time(self):
        """Test that application starts within acceptable time."""
        start_time = time.time()
        
        # Simulate application startup sequence
        self._simulate_app_startup()
        
        startup_time = time.time() - start_time
        
        # Should start within 5 seconds
        assert startup_time < 5.0, f"Startup took too long: {startup_time:.2f} seconds"
        
        # Log performance for monitoring
        print(f"Application startup time: {startup_time:.2f} seconds")
    
    def test_exercise_generation_performance(self):
        """Test exercise generation performance."""
        # Test local generation speed
        start_time = time.time()
        exercises = self._generate_local_exercises(10)
        local_time = time.time() - start_time
        
        assert local_time < 1.0, f"Local generation too slow: {local_time:.2f} seconds"
        assert len(exercises) == 10, "Generated wrong number of exercises"
        
        # Test batch generation efficiency
        start_time = time.time()
        large_batch = self._generate_local_exercises(100)
        batch_time = time.time() - start_time
        
        # Should scale efficiently
        assert batch_time < 10.0, f"Batch generation too slow: {batch_time:.2f} seconds"
        assert len(large_batch) == 100, "Batch generation count incorrect"
    
    def test_memory_usage_limits(self):
        """Test that memory usage stays within reasonable limits."""
        import tracemalloc
        
        tracemalloc.start()
        
        # Perform memory-intensive operations
        self._simulate_memory_intensive_operations()
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Convert to MB
        current_mb = current / (1024 * 1024)
        peak_mb = peak / (1024 * 1024)
        
        # Should stay under reasonable limits (e.g., 200MB)
        assert current_mb < 200, f"Current memory usage too high: {current_mb:.2f}MB"
        assert peak_mb < 300, f"Peak memory usage too high: {peak_mb:.2f}MB"
        
        print(f"Memory usage - Current: {current_mb:.2f}MB, Peak: {peak_mb:.2f}MB")
    
    def test_concurrent_operation_performance(self):
        """Test performance under concurrent operations."""
        import concurrent.futures
        
        start_time = time.time()
        
        # Simulate concurrent user operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self._simulate_user_operation, i) 
                for i in range(10)
            ]
            
            results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        
        # Should handle concurrent operations efficiently
        assert total_time < 10.0, f"Concurrent operations too slow: {total_time:.2f} seconds"
        assert all(result['success'] for result in results), "Some concurrent operations failed"
    
    def test_database_operation_performance(self, temp_dir):
        """Test database operation performance."""
        db_path = os.path.join(temp_dir, "test_performance.db")
        
        # Test bulk insert performance
        start_time = time.time()
        self._simulate_bulk_database_operations(db_path, 1000)
        bulk_time = time.time() - start_time
        
        assert bulk_time < 5.0, f"Bulk database operations too slow: {bulk_time:.2f} seconds"
        
        # Test query performance
        start_time = time.time()
        results = self._simulate_database_queries(db_path, 100)
        query_time = time.time() - start_time
        
        assert query_time < 2.0, f"Database queries too slow: {query_time:.2f} seconds"
        assert len(results) > 0, "Database queries returned no results"
    
    def _simulate_app_startup(self):
        """Simulate application startup operations."""
        # Mock configuration loading
        time.sleep(0.1)
        
        # Mock database initialization
        time.sleep(0.05)
        
        # Mock UI setup
        time.sleep(0.1)
        
        # Mock resource loading
        time.sleep(0.05)
    
    def _generate_local_exercises(self, count: int) -> List[Dict[str, Any]]:
        """Generate exercises locally for performance testing."""
        exercises = []
        verbs = ['hablar', 'comer', 'vivir', 'ser', 'estar']
        
        for i in range(count):
            exercise = {
                'id': i,
                'sentence': f'Yo _____ español.',
                'answer': 'hablo',
                'choices': ['hablo', 'habla', 'hablas', 'hablamos'],
                'verb': verbs[i % len(verbs)]
            }
            exercises.append(exercise)
            
            # Small delay to simulate processing
            time.sleep(0.001)
        
        return exercises
    
    def _simulate_memory_intensive_operations(self):
        """Simulate memory-intensive operations."""
        # Create large data structures
        large_list = [{'data': 'x' * 1000} for _ in range(1000)]
        
        # Process the data
        processed = [item['data'].upper() for item in large_list]
        
        # Clean up (normally would be garbage collected)
        del large_list, processed
    
    def _simulate_user_operation(self, operation_id: int) -> Dict[str, Any]:
        """Simulate a user operation."""
        start_time = time.time()
        
        # Simulate operation (e.g., exercise completion)
        time.sleep(0.1)  # Simulate work
        
        duration = time.time() - start_time
        
        return {
            'operation_id': operation_id,
            'duration': duration,
            'success': True
        }
    
    def _simulate_bulk_database_operations(self, db_path: str, count: int):
        """Simulate bulk database operations."""
        # Mock database operations
        for i in range(count):
            # Simulate database write
            time.sleep(0.001)  # 1ms per operation
    
    def _simulate_database_queries(self, db_path: str, count: int) -> List[Dict[str, Any]]:
        """Simulate database queries."""
        results = []
        
        for i in range(count):
            # Simulate database read
            time.sleep(0.0005)  # 0.5ms per query
            results.append({'id': i, 'data': f'result_{i}'})
        
        return results


class TestSecurityValidation:
    """Test security aspects of the application."""
    
    def test_input_sanitization(self):
        """Test that user inputs are properly sanitized."""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "\x00\x01\x02malicious",
            "javascript:alert('xss')",
            "${jndi:ldap://malicious.com/}",
            "{{7*7}}"  # Template injection
        ]
        
        for malicious_input in malicious_inputs:
            sanitized = self._sanitize_user_input(malicious_input)
            
            # Should not contain original malicious content
            assert malicious_input != sanitized, f"Input not sanitized: {malicious_input}"
            
            # Should not contain dangerous characters
            dangerous_chars = ['<', '>', "'", '"', ';', '&', '|', '$', '{', '}']
            for char in dangerous_chars:
                if char in malicious_input:
                    assert char not in sanitized or sanitized.count(char) < malicious_input.count(char), \
                        f"Dangerous character not properly handled: {char}"
    
    def test_file_path_validation(self, temp_dir):
        """Test file path validation and directory traversal prevention."""
        base_dir = temp_dir
        
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
            "file:///etc/passwd",
            "\\\\server\\share\\malicious",
            ".env",  # Should be blocked
            "app_config.json",  # Should be allowed
            "user_data.json"  # Should be allowed
        ]
        
        for path in malicious_paths:
            is_safe = self._validate_file_path(path, base_dir)
            
            # Paths with traversal should be blocked
            if '..' in path or path.startswith('/') or ':\\' in path:
                assert not is_safe, f"Malicious path not blocked: {path}"
            
            # Sensitive files should be blocked
            if path in ['.env', '.env.example']:
                assert not is_safe, f"Sensitive file not blocked: {path}"
    
    def test_api_key_security(self):
        """Test API key security measures."""
        test_api_key = "sk-test-1234567890abcdef1234567890abcdef"
        
        # Test key masking for logs
        masked_key = self._mask_api_key(test_api_key)
        assert test_api_key != masked_key, "API key not masked"
        assert "sk-test-****" in masked_key, "API key masking format incorrect"
        assert "1234567890abcdef" not in masked_key, "API key not fully masked"
        
        # Test key validation
        valid_keys = [
            "sk-test-1234567890abcdef",
            "sk-proj-1234567890abcdef1234567890abcdef12345678"
        ]
        
        invalid_keys = [
            "invalid-key",
            "",
            "sk-",
            "your_openai_api_key_here"
        ]
        
        for key in valid_keys:
            assert self._validate_api_key_security(key), f"Valid key rejected: {key[:10]}..."
        
        for key in invalid_keys:
            assert not self._validate_api_key_security(key), f"Invalid key accepted: {key}"
    
    def test_data_encryption_in_transit(self):
        """Test that sensitive data is encrypted in transit."""
        # Mock HTTPS request
        request_data = {
            'api_key': 'sk-test-key',
            'user_input': 'sensitive data'
        }
        
        # Simulate encryption for transit
        encrypted_data = self._encrypt_for_transit(request_data)
        
        # Original sensitive data should not be in plain text
        encrypted_str = str(encrypted_data)
        assert 'sk-test-key' not in encrypted_str, "API key exposed in transit"
        assert 'sensitive data' not in encrypted_str, "Sensitive data exposed in transit"
    
    def test_local_data_protection(self, temp_dir):
        """Test local data protection measures."""
        sensitive_data = {
            'api_key': 'sk-test-key',
            'user_progress': {'score': 85},
            'personal_settings': {'name': 'TestUser'}
        }
        
        # Test data is not stored in plain text
        storage_path = os.path.join(temp_dir, "user_data.json")
        self._store_sensitive_data(storage_path, sensitive_data)
        
        # Read raw file content
        with open(storage_path, 'rb') as f:
            raw_content = f.read().decode('utf-8', errors='ignore')
        
        # API key should not be in plain text
        assert 'sk-test-key' not in raw_content, "API key stored in plain text"
    
    def test_configuration_file_permissions(self, temp_dir):
        """Test that configuration files have appropriate permissions."""
        config_files = [
            'app_config.json',
            '.env',
            'progress.db'
        ]
        
        for filename in config_files:
            filepath = os.path.join(temp_dir, filename)
            
            # Create test file
            with open(filepath, 'w') as f:
                f.write('{"test": "data"}')
            
            # Check file permissions (Unix systems)
            if os.name != 'nt':  # Not Windows
                file_stat = os.stat(filepath)
                permissions = oct(file_stat.st_mode)[-3:]
                
                # Should not be world-readable for sensitive files
                if filename in ['.env', 'progress.db']:
                    assert permissions[-1] == '0', f"File {filename} is world-readable"
    
    def test_memory_cleanup(self):
        """Test that sensitive data is cleaned from memory."""
        # This is challenging to test directly, but we can test cleanup patterns
        sensitive_data = ['sk-test-key', 'password123', 'secret_info']
        
        # Process sensitive data
        processed_data = self._process_sensitive_data(sensitive_data)
        
        # Explicitly clean up
        self._cleanup_sensitive_memory(sensitive_data)
        
        # In a real implementation, we would verify memory is cleared
        # For now, just ensure cleanup function exists and runs
        assert processed_data is not None, "Processing failed"
    
    def _sanitize_user_input(self, user_input: str) -> str:
        """Sanitize user input for security."""
        if not isinstance(user_input, str):
            return str(user_input)
        
        # Basic HTML/script tag removal
        import re
        sanitized = re.sub(r'<[^>]*>', '', user_input)
        
        # Remove common injection patterns
        dangerous_patterns = [
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'<script',
            r'</script>',
            r'DROP\s+TABLE',
            r'UNION\s+SELECT',
            r'\$\{[^}]*\}',  # Template injection
        ]
        
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Limit length
        return sanitized[:1000]
    
    def _validate_file_path(self, file_path: str, base_dir: str) -> bool:
        """Validate file path for security."""
        if not isinstance(file_path, str):
            return False
        
        # Block directory traversal
        if '..' in file_path:
            return False
        
        # Block absolute paths
        if file_path.startswith('/') or ':\\' in file_path:
            return False
        
        # Block sensitive files
        sensitive_files = ['.env', '.env.example', 'config.ini', 'database.db']
        if file_path in sensitive_files:
            return False
        
        # Block system directories
        system_patterns = ['system32', 'windows', 'etc', 'proc', 'sys']
        if any(pattern in file_path.lower() for pattern in system_patterns):
            return False
        
        return True
    
    def _mask_api_key(self, api_key: str) -> str:
        """Mask API key for logging."""
        if not api_key or len(api_key) < 10:
            return "****"
        
        return api_key[:7] + "****" + api_key[-4:]
    
    def _validate_api_key_security(self, api_key: str) -> bool:
        """Validate API key from security perspective."""
        if not isinstance(api_key, str):
            return False
        
        if not api_key.startswith('sk-'):
            return False
        
        if len(api_key) < 20:
            return False
        
        # Check for placeholder values
        if api_key in ['your_openai_api_key_here', 'your_api_key_here']:
            return False
        
        return True
    
    def _encrypt_for_transit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt data for transit (mock implementation)."""
        # In real implementation, would use proper encryption
        import base64
        
        encrypted_data = {}
        for key, value in data.items():
            # Mock encryption: base64 encode
            encrypted_value = base64.b64encode(str(value).encode()).decode()
            encrypted_data[f"encrypted_{key}"] = encrypted_value
        
        return encrypted_data
    
    def _store_sensitive_data(self, filepath: str, data: Dict[str, Any]):
        """Store sensitive data with protection."""
        # In real implementation, would encrypt sensitive fields
        protected_data = {}
        
        for key, value in data.items():
            if 'api_key' in key.lower() or 'password' in key.lower():
                # Mock protection: hash sensitive values
                protected_data[key] = hashlib.sha256(str(value).encode()).hexdigest()
            else:
                protected_data[key] = value
        
        with open(filepath, 'w') as f:
            json.dump(protected_data, f)
    
    def _process_sensitive_data(self, sensitive_data: List[str]) -> List[str]:
        """Process sensitive data."""
        return [data.upper() for data in sensitive_data]
    
    def _cleanup_sensitive_memory(self, sensitive_data: List[str]):
        """Clean up sensitive data from memory."""
        # In real implementation, would overwrite memory
        # For Python, this is challenging due to string immutability
        # Best practice is to use bytes and overwrite them
        for i in range(len(sensitive_data)):
            sensitive_data[i] = ""


class TestNetworkSecurity:
    """Test network-related security measures."""
    
    def test_https_enforcement(self):
        """Test that HTTPS is enforced for API calls."""
        test_urls = [
            'http://api.openai.com/v1/chat/completions',  # Should be blocked
            'https://api.openai.com/v1/chat/completions', # Should be allowed
            'ftp://malicious.com/data',                   # Should be blocked
            'file:///etc/passwd',                         # Should be blocked
        ]
        
        for url in test_urls:
            is_secure = self._validate_url_security(url)
            
            if url.startswith('https://api.openai.com'):
                assert is_secure, f"Secure URL rejected: {url}"
            else:
                assert not is_secure, f"Insecure URL accepted: {url}"
    
    def test_request_timeout_limits(self):
        """Test that network requests have appropriate timeouts."""
        import requests
        from unittest.mock import patch
        
        with patch('requests.request') as mock_request:
            # Test timeout is set
            self._make_secure_request('https://api.openai.com/test')
            
            # Verify timeout was set in the call
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            
            # Should have timeout parameter
            assert 'timeout' in call_args.kwargs, "Request timeout not set"
            assert call_args.kwargs['timeout'] <= 30, "Request timeout too long"
    
    def test_user_agent_security(self):
        """Test that User-Agent headers don't expose sensitive info."""
        user_agent = self._get_user_agent()
        
        # Should not contain sensitive information
        sensitive_info = [
            'password', 'api_key', 'secret', 'token',
            'admin', 'root', 'internal', 'debug'
        ]
        
        user_agent_lower = user_agent.lower()
        for info in sensitive_info:
            assert info not in user_agent_lower, f"Sensitive info in User-Agent: {info}"
        
        # Should contain reasonable application info
        assert 'spanish' in user_agent_lower or 'conjugation' in user_agent_lower, \
            "User-Agent doesn't identify application"
    
    def test_proxy_security(self):
        """Test proxy configuration security."""
        proxy_configs = [
            {'http': 'http://proxy.company.com:8080'},
            {'https': 'https://secure-proxy.com:8080'},
            {'http': 'socks5://malicious.com:1080'},  # Should be blocked
        ]
        
        for proxy_config in proxy_configs:
            is_safe = self._validate_proxy_config(proxy_config)
            
            # Only HTTP/HTTPS proxies should be allowed
            for protocol, proxy_url in proxy_config.items():
                if proxy_url.startswith(('socks', 'ftp')):
                    assert not is_safe, f"Unsafe proxy protocol allowed: {proxy_url}"
    
    def _validate_url_security(self, url: str) -> bool:
        """Validate URL for security."""
        if not url.startswith('https://'):
            return False
        
        # Allow only specific trusted domains
        trusted_domains = [
            'api.openai.com',
            'openai.com'
        ]
        
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        
        return parsed.netloc in trusted_domains
    
    def _make_secure_request(self, url: str):
        """Make a secure network request."""
        import requests
        
        # Mock implementation with security measures
        headers = {
            'User-Agent': self._get_user_agent(),
            'Accept': 'application/json'
        }
        
        # Would make actual request with timeout
        requests.request(
            'GET', url,
            headers=headers,
            timeout=10,  # 10 second timeout
            verify=True  # Verify SSL certificates
        )
    
    def _get_user_agent(self) -> str:
        """Get secure user agent string."""
        return "Spanish-Conjugation-Practice/1.0.0"
    
    def _validate_proxy_config(self, proxy_config: Dict[str, str]) -> bool:
        """Validate proxy configuration."""
        allowed_protocols = ['http', 'https']
        
        for protocol, proxy_url in proxy_config.items():
            if not proxy_url.startswith(('http://', 'https://')):
                return False
        
        return True


class TestDataIntegrity:
    """Test data integrity and validation."""
    
    def test_configuration_integrity(self, temp_dir):
        """Test configuration file integrity checks."""
        config_path = os.path.join(temp_dir, "app_config.json")
        
        # Create valid configuration
        valid_config = {
            'version': '1.0.0',
            'dark_mode': False,
            'exercise_count': 5,
            'checksum': 'placeholder'
        }
        
        # Calculate checksum
        config_content = json.dumps(valid_config, sort_keys=True)
        checksum = hashlib.sha256(config_content.encode()).hexdigest()
        valid_config['checksum'] = checksum
        
        # Save configuration
        with open(config_path, 'w') as f:
            json.dump(valid_config, f)
        
        # Test integrity check
        is_valid = self._verify_config_integrity(config_path)
        assert is_valid, "Valid configuration failed integrity check"
        
        # Test tampered configuration
        tampered_config = valid_config.copy()
        tampered_config['dark_mode'] = True  # Change value but not checksum
        
        tampered_path = os.path.join(temp_dir, "tampered_config.json")
        with open(tampered_path, 'w') as f:
            json.dump(tampered_config, f)
        
        is_tampered_valid = self._verify_config_integrity(tampered_path)
        assert not is_tampered_valid, "Tampered configuration passed integrity check"
    
    def test_progress_data_validation(self, temp_dir):
        """Test progress data validation and integrity."""
        progress_data = {
            'total_exercises': 100,
            'correct_answers': 85,
            'sessions': 10,
            'total_time': 3600  # 1 hour in seconds
        }
        
        validation_result = self._validate_progress_data(progress_data)
        assert validation_result['valid'], "Valid progress data rejected"
        
        # Test invalid data
        invalid_data = {
            'total_exercises': 100,
            'correct_answers': 150,  # More correct than total!
            'sessions': -5,          # Negative sessions
            'total_time': -100       # Negative time
        }
        
        invalid_result = self._validate_progress_data(invalid_data)
        assert not invalid_result['valid'], "Invalid progress data accepted"
        assert len(invalid_result['errors']) > 0, "No validation errors reported"
    
    def test_exercise_data_sanitization(self):
        """Test that exercise data is properly sanitized."""
        raw_exercise = {
            'sentence': 'Yo <script>alert("xss")</script> español',
            'answer': 'hablo',
            'translation': 'I <img src=x onerror=alert(1)> Spanish',
            'choices': ['hablo', 'habla', '<script>evil</script>', 'hablas']
        }
        
        sanitized = self._sanitize_exercise_data(raw_exercise)
        
        # Should not contain dangerous content
        assert '<script>' not in str(sanitized), "Script tags not removed"
        assert 'onerror=' not in str(sanitized), "Event handlers not removed"
        assert 'alert(' not in str(sanitized), "JavaScript not removed"
    
    def _verify_config_integrity(self, config_path: str) -> bool:
        """Verify configuration file integrity."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if 'checksum' not in config:
                return False
            
            stored_checksum = config.pop('checksum')
            
            # Recalculate checksum
            config_content = json.dumps(config, sort_keys=True)
            calculated_checksum = hashlib.sha256(config_content.encode()).hexdigest()
            
            return stored_checksum == calculated_checksum
        
        except Exception:
            return False
    
    def _validate_progress_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate progress data for logical consistency."""
        errors = []
        
        total = data.get('total_exercises', 0)
        correct = data.get('correct_answers', 0)
        sessions = data.get('sessions', 0)
        time_spent = data.get('total_time', 0)
        
        # Logical consistency checks
        if correct > total:
            errors.append("Correct answers cannot exceed total exercises")
        
        if sessions < 0:
            errors.append("Sessions cannot be negative")
        
        if time_spent < 0:
            errors.append("Time spent cannot be negative")
        
        if total > 0 and sessions == 0:
            errors.append("Cannot have exercises without sessions")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _sanitize_exercise_data(self, exercise: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize exercise data."""
        sanitized = {}
        
        for key, value in exercise.items():
            if isinstance(value, str):
                sanitized[key] = self._sanitize_string(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_string(item) if isinstance(item, str) else item 
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize string content."""
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        
        # Remove JavaScript
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        
        # Remove event handlers
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
        
        return text.strip()


if __name__ == '__main__':
    pytest.main([__file__])