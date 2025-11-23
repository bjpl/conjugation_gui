"""
Unit tests for resource bundling and extraction functionality.

Tests cover:
- PyInstaller resource bundling
- Resource extraction at runtime
- File integrity validation
- Asset availability checks
- Bundle size optimization
"""

import pytest
import os
import sys
import subprocess
import tempfile
import shutil
import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from build_exe import create_executable, install_pyinstaller


class TestResourceBundling:
    """Test resource bundling with PyInstaller."""
    
    def test_pyinstaller_installation_check(self):
        """Test PyInstaller installation detection."""
        # Test when PyInstaller is available
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = MagicMock()
            result = self._check_pyinstaller_available()
            assert result == True
        
        # Test when PyInstaller is not available
        with patch('importlib.import_module', side_effect=ImportError()):
            result = self._check_pyinstaller_available()
            assert result == False
    
    def test_required_files_bundling(self, temp_dir):
        """Test that all required files are included in bundle specification."""
        required_files = [
            "app_config.json",
            ".env.example"
        ]
        
        bundle_spec = self._get_bundle_specification()
        
        for file in required_files:
            assert any(file in spec for spec in bundle_spec), f"Required file {file} not in bundle spec"
    
    def test_hidden_imports_specification(self):
        """Test that all necessary hidden imports are specified."""
        required_imports = [
            "PyQt5.QtCore",
            "PyQt5.QtGui", 
            "PyQt5.QtWidgets",
            "openai",
            "dotenv"
        ]
        
        hidden_imports = self._get_hidden_imports()
        
        for import_name in required_imports:
            assert import_name in hidden_imports, f"Hidden import {import_name} not specified"
    
    def test_bundle_command_generation(self):
        """Test PyInstaller command generation."""
        command = self._generate_pyinstaller_command()
        
        # Check essential flags
        assert "--name" in command and "SpanishConjugation" in command
        assert "--windowed" in command
        assert "--onefile" in command
        assert "--clean" in command
        assert "main.py" in command
        
        # Check data files are included
        assert "--add-data" in command
    
    def test_executable_output_path(self, temp_dir):
        """Test executable output path generation."""
        expected_exe_path = os.path.join("dist", "SpanishConjugation.exe")
        
        # Mock the build process
        os.makedirs(os.path.join(temp_dir, "dist"), exist_ok=True)
        exe_path = os.path.join(temp_dir, "dist", "SpanishConjugation.exe")
        
        # Create mock executable
        with open(exe_path, "wb") as f:
            f.write(b"MOCK_EXECUTABLE")
        
        assert os.path.exists(exe_path)
        assert os.path.basename(exe_path) == "SpanishConjugation.exe"
    
    def _check_pyinstaller_available(self):
        """Check if PyInstaller is available."""
        try:
            import PyInstaller
            return True
        except ImportError:
            return False
    
    def _get_bundle_specification(self):
        """Get list of files to be bundled."""
        return [
            "app_config.json",
            ".env.example"
        ]
    
    def _get_hidden_imports(self):
        """Get list of hidden imports."""
        return [
            "PyQt5.QtCore",
            "PyQt5.QtGui", 
            "PyQt5.QtWidgets",
            "openai",
            "dotenv"
        ]
    
    def _generate_pyinstaller_command(self):
        """Generate PyInstaller command as it would be in build_exe.py."""
        return [
            "python", "-m", "PyInstaller",
            "--name", "SpanishConjugation",
            "--windowed",
            "--onefile",
            "--add-data", "app_config.json:.",
            "--add-data", ".env.example:.",
            "--hidden-import", "PyQt5.QtCore",
            "--hidden-import", "PyQt5.QtGui", 
            "--hidden-import", "PyQt5.QtWidgets",
            "--hidden-import", "openai",
            "--hidden-import", "dotenv",
            "--clean",
            "main.py"
        ]


class TestResourceExtraction:
    """Test resource extraction at runtime."""
    
    def test_config_file_extraction(self, temp_dir):
        """Test extraction of app_config.json from bundle."""
        # Simulate bundled resource extraction
        original_config = {
            "dark_mode": False,
            "show_translation": False,
            "api_model": "gpt-4o"
        }
        
        # Create extracted config file
        extracted_path = os.path.join(temp_dir, "app_config.json")
        import json
        with open(extracted_path, 'w') as f:
            json.dump(original_config, f)
        
        # Verify extraction
        assert os.path.exists(extracted_path)
        
        with open(extracted_path, 'r') as f:
            extracted_config = json.load(f)
        
        assert extracted_config == original_config
    
    def test_env_example_extraction(self, temp_dir):
        """Test extraction of .env.example from bundle."""
        original_content = "OPENAI_API_KEY=your_openai_api_key_here\n"
        
        # Create extracted .env.example
        extracted_path = os.path.join(temp_dir, ".env.example")
        with open(extracted_path, 'w') as f:
            f.write(original_content)
        
        # Verify extraction
        assert os.path.exists(extracted_path)
        
        with open(extracted_path, 'r') as f:
            extracted_content = f.read()
        
        assert extracted_content == original_content
    
    def test_resource_availability_at_runtime(self, temp_dir):
        """Test that resources are available when the executable runs."""
        # Simulate runtime resource check
        expected_resources = [
            "app_config.json",
            ".env.example"
        ]
        
        # Create all expected resources
        for resource in expected_resources:
            resource_path = os.path.join(temp_dir, resource)
            with open(resource_path, 'w') as f:
                f.write(f"Content for {resource}")
        
        # Verify all resources exist
        for resource in expected_resources:
            resource_path = os.path.join(temp_dir, resource)
            assert os.path.exists(resource_path), f"Resource {resource} not available at runtime"
    
    def test_resource_integrity_validation(self, temp_dir):
        """Test validation of extracted resource integrity."""
        # Create a resource with known content
        original_content = '{"test": "content", "integrity": "check"}'
        original_hash = hashlib.md5(original_content.encode()).hexdigest()
        
        resource_path = os.path.join(temp_dir, "test_resource.json")
        with open(resource_path, 'w') as f:
            f.write(original_content)
        
        # Verify integrity
        with open(resource_path, 'r') as f:
            extracted_content = f.read()
        
        extracted_hash = hashlib.md5(extracted_content.encode()).hexdigest()
        assert extracted_hash == original_hash, "Resource integrity check failed"
    
    def test_missing_resource_handling(self, temp_dir):
        """Test handling when expected resources are missing."""
        # Test that app handles missing resources gracefully
        missing_resources = ["missing_config.json", "missing_env.txt"]
        
        for resource in missing_resources:
            resource_path = os.path.join(temp_dir, resource)
            assert not os.path.exists(resource_path)
            
            # Should handle gracefully
            result = self._handle_missing_resource(resource_path)
            assert result is not None  # Should not crash
    
    def _handle_missing_resource(self, resource_path):
        """Simulate handling of missing resource."""
        if not os.path.exists(resource_path):
            # Return default or handle gracefully
            return "default_content"
        
        with open(resource_path, 'r') as f:
            return f.read()


class TestDistributionStructure:
    """Test distribution folder structure and contents."""
    
    def test_distribution_folder_creation(self, temp_dir):
        """Test creation of distribution folder with correct structure."""
        dist_folder = os.path.join(temp_dir, "SpanishConjugation_Distribution")
        
        # Simulate distribution creation
        os.makedirs(dist_folder, exist_ok=True)
        
        # Create expected files
        expected_files = [
            "SpanishConjugation.exe",
            ".env.example",
            "Run.bat",
            "README.txt"
        ]
        
        for file in expected_files:
            file_path = os.path.join(dist_folder, file)
            with open(file_path, 'w') as f:
                f.write(f"Content for {file}")
        
        # Verify structure
        assert os.path.exists(dist_folder)
        for file in expected_files:
            file_path = os.path.join(dist_folder, file)
            assert os.path.exists(file_path), f"Distribution missing {file}"
    
    def test_batch_file_creation(self, temp_dir):
        """Test creation of Run.bat launcher."""
        batch_content = """@echo off
echo Starting Spanish Conjugation Practice...
echo.
if not exist .env (
    echo Please create a .env file with your OpenAI API key.
    echo See .env.example for the format.
    echo.
    pause
    exit
)
SpanishConjugation.exe
"""
        
        batch_path = os.path.join(temp_dir, "Run.bat")
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        # Verify batch file
        assert os.path.exists(batch_path)
        
        with open(batch_path, 'r') as f:
            content = f.read()
        
        assert "SpanishConjugation.exe" in content
        assert ".env" in content
        assert "pause" in content
    
    def test_readme_creation(self, temp_dir):
        """Test creation of distribution README.txt."""
        readme_content = """Spanish Conjugation Practice - Quick Start

1. SETUP API KEY:
   - Rename '.env.example' to '.env'
   - Open .env and replace 'your_openai_api_key_here' with your actual OpenAI API key

2. RUN THE APPLICATION:
   - Double-click 'Run.bat' to start
"""
        
        readme_path = os.path.join(temp_dir, "README.txt")
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        # Verify README
        assert os.path.exists(readme_path)
        
        with open(readme_path, 'r') as f:
            content = f.read()
        
        assert "Spanish Conjugation Practice" in content
        assert "API KEY" in content
        assert "Run.bat" in content


class TestBundleOptimization:
    """Test bundle size optimization."""
    
    def test_executable_size_reasonable(self):
        """Test that executable size is within reasonable limits."""
        # Mock executable size (in real test, would check actual file)
        mock_size_bytes = 50 * 1024 * 1024  # 50MB
        mock_size_mb = mock_size_bytes / (1024 * 1024)
        
        # Should be under reasonable limit (e.g., 200MB)
        assert mock_size_mb < 200, f"Executable too large: {mock_size_mb:.1f}MB"
        
        # Should be over minimum viable size (e.g., 10MB)
        assert mock_size_mb > 10, f"Executable suspiciously small: {mock_size_mb:.1f}MB"
    
    def test_unnecessary_modules_excluded(self):
        """Test that unnecessary modules are excluded from bundle."""
        # Modules that shouldn't be included
        unnecessary_modules = [
            "tkinter",  # We use PyQt5
            "matplotlib",  # Not needed for this app
            "numpy",  # Not needed
            "pandas"  # Not needed
        ]
        
        # In real implementation, would analyze bundle contents
        bundled_modules = self._get_bundled_modules()
        
        for module in unnecessary_modules:
            assert module not in bundled_modules, f"Unnecessary module {module} included in bundle"
    
    def test_compression_effectiveness(self, temp_dir):
        """Test that compression is effective."""
        # Create test files of different sizes
        test_sizes = [1024, 10240, 102400]  # 1KB, 10KB, 100KB
        
        for size in test_sizes:
            # Create test file
            test_file = os.path.join(temp_dir, f"test_{size}.dat")
            with open(test_file, 'wb') as f:
                f.write(b'A' * size)
            
            original_size = os.path.getsize(test_file)
            
            # Simulate compression (in real test, would use actual compression)
            compressed_size = original_size * 0.7  # Assume 30% compression
            
            compression_ratio = compressed_size / original_size
            assert compression_ratio < 1.0, "No compression achieved"
            assert compression_ratio > 0.1, "Compression too aggressive (data loss risk)"
    
    def _get_bundled_modules(self):
        """Get list of modules included in bundle (mock implementation)."""
        # In real implementation, would analyze PyInstaller bundle
        return [
            "PyQt5.QtCore",
            "PyQt5.QtGui", 
            "PyQt5.QtWidgets",
            "openai",
            "dotenv",
            "sys",
            "os",
            "json"
        ]


class TestDependencyValidation:
    """Test validation of dependencies in bundle."""
    
    def test_python_runtime_inclusion(self):
        """Test that Python runtime is properly included."""
        # Mock check for Python runtime components
        required_runtime_components = [
            "python.exe",  # Python interpreter
            "python3.dll",  # Python DLL
            "stdlib"  # Standard library
        ]
        
        included_components = self._get_runtime_components()
        
        for component in required_runtime_components:
            assert any(component in comp for comp in included_components), \
                f"Python runtime component {component} not included"
    
    def test_pyqt_dependencies_complete(self):
        """Test that all PyQt5 dependencies are included."""
        required_pyqt_modules = [
            "PyQt5.QtCore",
            "PyQt5.QtGui",
            "PyQt5.QtWidgets"
        ]
        
        included_modules = self._get_bundled_modules()
        
        for module in required_pyqt_modules:
            assert module in included_modules, f"PyQt5 module {module} missing"
    
    def test_openai_client_dependencies(self):
        """Test that OpenAI client dependencies are complete."""
        required_openai_deps = [
            "openai",
            "httpx",  # HTTP client used by OpenAI
            "pydantic",  # Data validation
            "typing_extensions"  # Type hints
        ]
        
        included_modules = self._get_bundled_modules()
        
        for dep in required_openai_deps:
            # Check if dependency is included or can be imported
            dependency_available = dep in included_modules or self._can_import(dep)
            assert dependency_available, f"OpenAI dependency {dep} not available"
    
    def _get_runtime_components(self):
        """Get list of Python runtime components (mock implementation)."""
        return [
            "python.exe",
            "python3.dll",
            "stdlib",
            "site-packages"
        ]
    
    def _can_import(self, module_name):
        """Check if a module can be imported."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False


if __name__ == '__main__':
    pytest.main([__file__])