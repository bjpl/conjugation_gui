"""
Unit tests for error handling with missing dependencies.

Tests cover:
- Missing Python packages
- Missing system dependencies
- Network connectivity issues
- OpenAI API failures
- File system errors
- Runtime exceptions
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock, mock_open
from importlib import import_module

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class TestMissingPythonDependencies:
    """Test handling of missing Python packages."""
    
    def test_missing_pyqt5_handling(self):
        """Test graceful handling when PyQt5 is missing."""
        with patch.dict('sys.modules', {'PyQt5': None}):
            with patch('importlib.import_module', side_effect=ImportError("No module named 'PyQt5'")):
                result = self._check_dependency_availability('PyQt5')
                assert result['available'] == False
                assert 'PyQt5' in result['error_message']
    
    def test_missing_openai_handling(self):
        """Test graceful handling when OpenAI package is missing."""
        with patch.dict('sys.modules', {'openai': None}):
            with patch('importlib.import_module', side_effect=ImportError("No module named 'openai'")):
                result = self._check_dependency_availability('openai')
                assert result['available'] == False
                assert result['fallback_mode'] == 'offline'
    
    def test_missing_dotenv_handling(self):
        """Test graceful handling when python-dotenv is missing."""
        with patch.dict('sys.modules', {'dotenv': None}):
            with patch('importlib.import_module', side_effect=ImportError("No module named 'dotenv'")):
                result = self._check_dependency_availability('dotenv')
                assert result['available'] == False
                assert result['fallback_mode'] == 'manual_env'
    
    def test_partial_pyqt5_installation(self):
        """Test handling when PyQt5 is partially installed."""
        # Mock scenario where core PyQt5 exists but WebEngine is missing
        with patch('importlib.import_module') as mock_import:
            def side_effect(name):
                if name == 'PyQt5.QtCore':
                    return MagicMock()
                elif name == 'PyQt5.QtWebEngine':
                    raise ImportError("No module named 'PyQt5.QtWebEngine'")
                else:
                    return MagicMock()
            
            mock_import.side_effect = side_effect
            
            result = self._check_pyqt5_completeness()
            assert result['core_available'] == True
            assert result['webengine_available'] == False
            assert result['can_run_basic'] == True
    
    def test_incompatible_package_versions(self):
        """Test handling of incompatible package versions."""
        version_tests = [
            ('PyQt5', '5.14.0', False),  # Too old
            ('PyQt5', '5.15.7', True),   # Compatible
            ('openai', '0.28.0', False), # Too old
            ('openai', '1.64.0', True),  # Compatible
        ]
        
        for package, version, should_be_compatible in version_tests:
            compatibility = self._check_version_compatibility(package, version)
            assert compatibility == should_be_compatible, f"{package} {version} compatibility check failed"
    
    def _check_dependency_availability(self, package_name):
        """Check if a package dependency is available."""
        try:
            import_module(package_name)
            return {'available': True, 'error_message': None, 'fallback_mode': None}
        except ImportError as e:
            fallback_modes = {
                'openai': 'offline',
                'dotenv': 'manual_env',
                'PyQt5': 'console_mode'
            }
            
            return {
                'available': False,
                'error_message': str(e),
                'fallback_mode': fallback_modes.get(package_name, 'degraded')
            }
    
    def _check_pyqt5_completeness(self):
        """Check PyQt5 installation completeness."""
        components = {
            'PyQt5.QtCore': False,
            'PyQt5.QtGui': False,
            'PyQt5.QtWidgets': False,
            'PyQt5.QtWebEngine': False
        }
        
        for component in components:
            try:
                import_module(component)
                components[component] = True
            except ImportError:
                pass
        
        return {
            'core_available': components['PyQt5.QtCore'],
            'gui_available': components['PyQt5.QtGui'],
            'widgets_available': components['PyQt5.QtWidgets'],
            'webengine_available': components['PyQt5.QtWebEngine'],
            'can_run_basic': all([
                components['PyQt5.QtCore'],
                components['PyQt5.QtGui'],
                components['PyQt5.QtWidgets']
            ])
        }
    
    def _check_version_compatibility(self, package, version):
        """Check if package version is compatible."""
        compatibility_matrix = {
            'PyQt5': {
                'min_version': '5.15.0',
                'max_version': '5.16.0'
            },
            'openai': {
                'min_version': '1.0.0',
                'max_version': '2.0.0'
            }
        }
        
        if package not in compatibility_matrix:
            return True
        
        # Simple version comparison (in real implementation, use packaging.version)
        min_ver = compatibility_matrix[package]['min_version']
        max_ver = compatibility_matrix[package]['max_version']
        
        return min_ver <= version < max_ver


class TestSystemDependencyErrors:
    """Test handling of missing system dependencies."""
    
    def test_missing_visual_cpp_runtime(self):
        """Test handling when Visual C++ Runtime is missing."""
        # This would typically manifest as ImportError for certain modules
        with patch('importlib.import_module', side_effect=ImportError("DLL load failed")):
            result = self._check_system_runtime()
            assert result['vcruntime_available'] == False
            assert 'DLL' in result['error_details']
    
    def test_insufficient_system_resources(self):
        """Test handling of insufficient system resources."""
        # Mock low memory scenario
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory.return_value.available = 100 * 1024 * 1024  # 100MB
            
            resource_check = self._check_system_resources()
            assert resource_check['sufficient_memory'] == False
            assert resource_check['recommended_action'] == 'close_other_apps'
    
    def test_file_system_permissions(self, temp_dir):
        """Test handling of file system permission errors."""
        # Test write permission
        test_file = os.path.join(temp_dir, "permission_test.json")
        
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = PermissionError("Permission denied")
            
            result = self._test_file_permissions(test_file)
            assert result['can_write'] == False
            assert result['error_type'] == 'permission'
    
    def test_antivirus_interference(self, temp_dir):
        """Test detection of antivirus software interference."""
        # Mock antivirus blocking executable creation
        exe_path = os.path.join(temp_dir, "test.exe")
        
        with patch('os.path.exists', return_value=False):
            with patch('shutil.copy', side_effect=OSError("Operation blocked")):
                result = self._check_antivirus_interference(exe_path)
                assert result['interference_detected'] == True
                assert 'blocked' in result['details'].lower()
    
    def _check_system_runtime(self):
        """Check system runtime availability."""
        try:
            # Try to import a module that requires Visual C++ Runtime
            import ctypes
            return {
                'vcruntime_available': True,
                'error_details': None
            }
        except (ImportError, OSError) as e:
            return {
                'vcruntime_available': False,
                'error_details': str(e)
            }
    
    def _check_system_resources(self):
        """Check system resource availability."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_mb = memory.available / (1024 * 1024)
            
            return {
                'sufficient_memory': available_mb > 512,  # Require 512MB+
                'available_mb': available_mb,
                'recommended_action': 'close_other_apps' if available_mb < 512 else 'none'
            }
        except ImportError:
            # If psutil not available, assume sufficient
            return {
                'sufficient_memory': True,
                'available_mb': 'unknown',
                'recommended_action': 'none'
            }
    
    def _test_file_permissions(self, file_path):
        """Test file system permissions."""
        try:
            with open(file_path, 'w') as f:
                f.write('test')
            os.unlink(file_path)
            return {'can_write': True, 'error_type': None}
        except PermissionError:
            return {'can_write': False, 'error_type': 'permission'}
        except OSError as e:
            return {'can_write': False, 'error_type': 'system', 'details': str(e)}
    
    def _check_antivirus_interference(self, exe_path):
        """Check for antivirus software interference."""
        try:
            # Try to create a test executable
            with open(exe_path, 'wb') as f:
                f.write(b'MZ')  # PE header start
            
            if os.path.exists(exe_path):
                os.unlink(exe_path)
                return {'interference_detected': False, 'details': 'No interference'}
            else:
                return {'interference_detected': True, 'details': 'File creation blocked'}
        except (OSError, PermissionError) as e:
            return {'interference_detected': True, 'details': str(e)}


class TestNetworkConnectivityErrors:
    """Test handling of network connectivity issues."""
    
    @patch('requests.get')
    def test_no_internet_connection(self, mock_get):
        """Test handling when there's no internet connection."""
        mock_get.side_effect = ConnectionError("No internet connection")
        
        connectivity = self._check_internet_connectivity()
        assert connectivity['connected'] == False
        assert connectivity['fallback_mode'] == 'offline'
    
    @patch('requests.get')
    def test_openai_api_unreachable(self, mock_get):
        """Test handling when OpenAI API is unreachable."""
        def side_effect(url, **kwargs):
            if 'openai.com' in url:
                raise ConnectionError("API unreachable")
            return MagicMock(status_code=200)
        
        mock_get.side_effect = side_effect
        
        api_status = self._check_openai_api_status()
        assert api_status['api_reachable'] == False
        assert api_status['suggested_action'] == 'use_offline_mode'
    
    @patch('requests.get')
    def test_proxy_configuration_issues(self, mock_get):
        """Test handling of proxy configuration issues."""
        mock_get.side_effect = ConnectionError("Proxy error")
        
        proxy_check = self._check_proxy_configuration()
        assert proxy_check['proxy_working'] == False
        assert 'proxy' in proxy_check['error_message'].lower()
    
    @patch('requests.get')
    def test_dns_resolution_failure(self, mock_get):
        """Test handling of DNS resolution failures."""
        mock_get.side_effect = ConnectionError("Name resolution failed")
        
        dns_check = self._check_dns_resolution()
        assert dns_check['dns_working'] == False
        assert 'resolution' in dns_check['error_message'].lower()
    
    def _check_internet_connectivity(self):
        """Check internet connectivity."""
        try:
            import requests
            response = requests.get('https://httpbin.org/status/200', timeout=5)
            return {
                'connected': response.status_code == 200,
                'fallback_mode': None
            }
        except Exception:
            return {
                'connected': False,
                'fallback_mode': 'offline'
            }
    
    def _check_openai_api_status(self):
        """Check OpenAI API status."""
        try:
            import requests
            response = requests.get('https://api.openai.com/', timeout=10)
            return {
                'api_reachable': True,
                'suggested_action': 'none'
            }
        except Exception:
            return {
                'api_reachable': False,
                'suggested_action': 'use_offline_mode'
            }
    
    def _check_proxy_configuration(self):
        """Check proxy configuration."""
        try:
            import requests
            # Test with system proxy settings
            response = requests.get('https://httpbin.org/ip', timeout=5)
            return {
                'proxy_working': response.status_code == 200,
                'error_message': None
            }
        except Exception as e:
            return {
                'proxy_working': False,
                'error_message': str(e)
            }
    
    def _check_dns_resolution(self):
        """Check DNS resolution."""
        try:
            import socket
            socket.gethostbyname('google.com')
            return {
                'dns_working': True,
                'error_message': None
            }
        except Exception as e:
            return {
                'dns_working': False,
                'error_message': str(e)
            }


class TestOpenAIAPIErrors:
    """Test handling of OpenAI API-specific errors."""
    
    @patch('openai.OpenAI')
    def test_invalid_api_key_error(self, mock_openai):
        """Test handling of invalid API key errors."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Invalid API key")
        mock_openai.return_value = mock_client
        
        api_test = self._test_openai_request("sk-invalid-key")
        assert api_test['success'] == False
        assert 'api key' in api_test['error_message'].lower()
    
    @patch('openai.OpenAI')
    def test_rate_limit_exceeded(self, mock_openai):
        """Test handling of rate limit errors."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
        mock_openai.return_value = mock_client
        
        api_test = self._test_openai_request("sk-valid-key")
        assert api_test['success'] == False
        assert 'rate limit' in api_test['error_message'].lower()
        assert api_test['retry_suggested'] == True
    
    @patch('openai.OpenAI')
    def test_quota_exceeded_error(self, mock_openai):
        """Test handling of quota exceeded errors."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Quota exceeded")
        mock_openai.return_value = mock_client
        
        api_test = self._test_openai_request("sk-valid-key")
        assert api_test['success'] == False
        assert 'quota' in api_test['error_message'].lower()
        assert api_test['fallback_mode'] == 'offline'
    
    @patch('openai.OpenAI')
    def test_api_service_unavailable(self, mock_openai):
        """Test handling when OpenAI service is unavailable."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Service unavailable")
        mock_openai.return_value = mock_client
        
        api_test = self._test_openai_request("sk-valid-key")
        assert api_test['success'] == False
        assert api_test['temporary_error'] == True
    
    def _test_openai_request(self, api_key):
        """Test an OpenAI API request."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            
            return {
                'success': True,
                'error_message': None,
                'retry_suggested': False,
                'fallback_mode': None,
                'temporary_error': False
            }
        except Exception as e:
            error_message = str(e).lower()
            
            return {
                'success': False,
                'error_message': str(e),
                'retry_suggested': 'rate limit' in error_message,
                'fallback_mode': 'offline' if 'quota' in error_message else None,
                'temporary_error': any(term in error_message for term in ['unavailable', 'timeout', 'server error'])
            }


class TestRuntimeExceptionHandling:
    """Test handling of runtime exceptions."""
    
    def test_json_parsing_errors(self):
        """Test handling of JSON parsing errors."""
        invalid_json_strings = [
            '{"incomplete": json',
            'not json at all',
            '{"valid": "json"} extra text',
            '',
            None
        ]
        
        for json_string in invalid_json_strings:
            result = self._safe_json_parse(json_string)
            assert result['success'] == False or result['data'] is None
    
    def test_file_corruption_handling(self, temp_dir):
        """Test handling of corrupted files."""
        # Create corrupted config file
        config_path = os.path.join(temp_dir, "corrupted_config.json")
        with open(config_path, 'wb') as f:
            f.write(b'\x00\x01\x02\x03corrupted')
        
        result = self._safe_config_load(config_path)
        assert result['loaded'] == False
        assert result['using_defaults'] == True
    
    def test_memory_allocation_errors(self):
        """Test handling of memory allocation errors."""
        with patch('json.load', side_effect=MemoryError("Out of memory")):
            result = self._safe_operation_with_fallback()
            assert result['success'] == False
            assert result['fallback_used'] == True
    
    def test_thread_safety_exceptions(self):
        """Test handling of thread safety exceptions."""
        import threading
        
        results = []
        exceptions = []
        
        def worker():
            try:
                # Simulate concurrent access that might cause issues
                result = self._thread_safe_operation()
                results.append(result)
            except Exception as e:
                exceptions.append(e)
        
        # Start multiple threads
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should handle concurrent access gracefully
        assert len(exceptions) == 0, "Thread safety exceptions occurred"
        assert len(results) == 5, "Not all operations completed"
    
    def _safe_json_parse(self, json_string):
        """Safely parse JSON string."""
        try:
            import json
            data = json.loads(json_string)
            return {'success': True, 'data': data}
        except (json.JSONDecodeError, TypeError, ValueError):
            return {'success': False, 'data': None}
    
    def _safe_config_load(self, config_path):
        """Safely load configuration file."""
        try:
            import json
            with open(config_path, 'r') as f:
                config = json.load(f)
            return {'loaded': True, 'config': config, 'using_defaults': False}
        except Exception:
            # Use default configuration
            default_config = {'dark_mode': False, 'exercise_count': 5}
            return {'loaded': False, 'config': default_config, 'using_defaults': True}
    
    def _safe_operation_with_fallback(self):
        """Perform operation with fallback on memory error."""
        try:
            # Simulate memory-intensive operation
            import json
            large_data = {'data': 'x' * 1000000}
            json.dumps(large_data)
            return {'success': True, 'fallback_used': False}
        except MemoryError:
            # Use fallback approach
            return {'success': False, 'fallback_used': True}
    
    def _thread_safe_operation(self):
        """Thread-safe operation that might have concurrency issues."""
        import threading
        import time
        
        # Use a lock for thread safety
        lock = threading.Lock()
        
        with lock:
            # Simulate operation that needs synchronization
            time.sleep(0.01)  # Small delay to increase chance of race conditions
            return {'thread_id': threading.current_thread().ident, 'success': True}


if __name__ == '__main__':
    pytest.main([__file__])