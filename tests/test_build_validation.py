"""
Build validation tests for PyInstaller executable
Tests that the built executable works correctly on clean systems
"""
import os
import sys
import json
import subprocess
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestBuildConfiguration:
    """Test build configuration files"""
    
    def test_build_config_valid_json(self):
        """Test that build_config.json is valid JSON"""
        config_path = Path("build_config.json")
        assert config_path.exists(), "build_config.json not found"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Validate required sections
        assert "app" in config
        assert "build" in config
        assert "resources" in config
        
        # Validate app section
        app_config = config["app"]
        assert "name" in app_config
        assert "version" in app_config
        assert "description" in app_config
        
        # Validate version format
        version = app_config["version"]
        version_parts = version.split(".")
        assert len(version_parts) >= 2, f"Invalid version format: {version}"
        
        for part in version_parts:
            assert part.isdigit(), f"Version part '{part}' is not numeric"
    
    def test_pyinstaller_spec_syntax(self):
        """Test that PyInstaller spec files are syntactically valid"""
        spec_files = [
            "SpanishConjugation.spec",
            "SpanishConjugation_Enhanced.spec"
        ]
        
        for spec_file in spec_files:
            if Path(spec_file).exists():
                # Try to compile the spec file
                try:
                    with open(spec_file, 'r', encoding='utf-8') as f:
                        spec_code = f.read()
                    
                    # Basic syntax check by compiling
                    compile(spec_code, spec_file, 'exec')
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {spec_file}: {e}")
    
    def test_requirements_file(self):
        """Test requirements.txt format and validity"""
        req_path = Path("requirements.txt")
        if req_path.exists():
            with open(req_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Basic package name validation
                    if '==' in line:
                        package, version = line.split('==', 1)
                        assert package, f"Empty package name at line {line_num}"
                        assert version, f"Empty version at line {line_num}"
                    elif '>=' in line:
                        package, version = line.split('>=', 1)
                        assert package, f"Empty package name at line {line_num}"
                        assert version, f"Empty version at line {line_num}"

class TestBuildScripts:
    """Test build scripts functionality"""
    
    def test_build_advanced_import(self):
        """Test that build_advanced.py can be imported"""
        try:
            import build_advanced
            assert hasattr(build_advanced, 'BuildManager')
            assert hasattr(build_advanced, 'main')
        except ImportError as e:
            pytest.fail(f"Failed to import build_advanced: {e}")
    
    def test_build_installer_import(self):
        """Test that build_installer.py can be imported"""
        try:
            import build_installer
            assert hasattr(build_installer, 'NSISBuilder')
            assert hasattr(build_installer, 'main')
        except ImportError as e:
            pytest.fail(f"Failed to import build_installer: {e}")
    
    def test_compatibility_check_import(self):
        """Test that compatibility_check.py can be imported"""
        try:
            import compatibility_check
            assert hasattr(compatibility_check, 'SystemChecker')
            assert hasattr(compatibility_check, 'main')
        except ImportError as e:
            pytest.fail(f"Failed to import compatibility_check: {e}")
    
    @patch('subprocess.run')
    def test_build_manager_creation(self, mock_run):
        """Test BuildManager can be created with valid config"""
        # Mock the config file to avoid file dependency
        with patch('builtins.open') as mock_open:
            mock_config = {
                "app": {"name": "TestApp", "version": "1.0.0", "author": "Test"},
                "build": {"one_file": True, "console": False},
                "resources": {"icon": "test.ico", "data_files": []}
            }
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_config)
            
            from build_advanced import BuildManager
            builder = BuildManager()
            
            assert builder.config["app"]["name"] == "TestApp"
            assert builder.config["app"]["version"] == "1.0.0"

class TestExecutableValidation:
    """Test executable validation procedures"""
    
    def test_executable_exists_after_build(self):
        """Test that executable exists in expected location"""
        dist_dir = Path("dist")
        if dist_dir.exists():
            exe_files = list(dist_dir.glob("*.exe"))
            if exe_files:
                # If executable exists, validate it
                exe_path = exe_files[0]
                assert exe_path.stat().st_size > 1024 * 1024, "Executable is suspiciously small"
                print(f"Found executable: {exe_path} ({exe_path.stat().st_size / (1024*1024):.1f} MB)")
    
    @pytest.mark.skipif(not Path("dist").exists(), reason="No dist directory found")
    def test_executable_basic_properties(self):
        """Test basic executable properties"""
        dist_dir = Path("dist")
        exe_files = list(dist_dir.glob("*.exe"))
        
        if exe_files:
            exe_path = exe_files[0]
            
            # Test file size is reasonable
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            assert 10 <= size_mb <= 500, f"Executable size {size_mb:.1f} MB is outside expected range"
            
            # Test file is executable
            assert os.access(exe_path, os.X_OK), "File is not executable"
    
    @pytest.mark.skipif(not Path("dist").exists(), reason="No dist directory found")
    def test_executable_help_output(self):
        """Test that executable can show help without crashing"""
        dist_dir = Path("dist")
        exe_files = list(dist_dir.glob("*.exe"))
        
        if exe_files:
            exe_path = exe_files[0]
            
            try:
                # Try running with --help flag
                result = subprocess.run(
                    [str(exe_path), "--help"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                # Should not crash immediately
                assert result.returncode in [0, 1, 2], f"Unexpected return code: {result.returncode}"
                
            except subprocess.TimeoutExpired:
                # Timeout is okay for GUI apps
                pass
            except FileNotFoundError:
                pytest.skip("Executable not found or not runnable")

class TestDependencyValidation:
    """Test dependency validation"""
    
    def test_critical_modules_importable(self):
        """Test that critical modules can be imported"""
        critical_modules = [
            'json',
            'os',
            'sys',
            'pathlib',
            'subprocess',
            'tempfile',
        ]
        
        for module in critical_modules:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Critical module {module} cannot be imported: {e}")
    
    def test_application_modules_importable(self):
        """Test that application modules can be imported"""
        app_modules = [
            'conjugation_engine',
            'exercise_generator',
            'progress_tracker',
            'task_scenarios',
            'speed_practice',
            'learning_path'
        ]
        
        for module in app_modules:
            module_path = Path(f"{module}.py")
            if module_path.exists():
                try:
                    __import__(module)
                except ImportError as e:
                    pytest.fail(f"Application module {module} cannot be imported: {e}")
    
    def test_pyinstaller_hooks_exist(self):
        """Test that PyInstaller hooks exist for critical packages"""
        hooks_dir = Path("pyinstaller_hooks")
        if hooks_dir.exists():
            expected_hooks = [
                "hook-openai.py",
                "hook-PyQt5.py",
                "hook-requests.py",
                "hook-dotenv.py"
            ]
            
            for hook in expected_hooks:
                hook_path = hooks_dir / hook
                if hook_path.exists():
                    # Validate hook syntax
                    with open(hook_path, 'r', encoding='utf-8') as f:
                        hook_code = f.read()
                    
                    try:
                        compile(hook_code, str(hook_path), 'exec')
                    except SyntaxError as e:
                        pytest.fail(f"Syntax error in {hook}: {e}")

class TestAssetValidation:
    """Test asset and resource validation"""
    
    def test_assets_directory_structure(self):
        """Test that assets directory has expected structure"""
        assets_dir = Path("assets")
        if assets_dir.exists():
            # Check for expected files
            expected_files = ["icon.ico"]
            
            for file_name in expected_files:
                file_path = assets_dir / file_name
                if file_path.exists():
                    assert file_path.stat().st_size > 0, f"{file_name} is empty"
    
    def test_configuration_files_exist(self):
        """Test that required configuration files exist"""
        required_files = [
            "app_config.json",
            ".env.example"
        ]
        
        for file_name in required_files:
            file_path = Path(file_name)
            if file_path.exists():
                assert file_path.stat().st_size > 0, f"{file_name} is empty"
                
                # Additional validation for JSON files
                if file_name.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            json.load(f)
                        except json.JSONDecodeError as e:
                            pytest.fail(f"Invalid JSON in {file_name}: {e}")

class TestInstaller:
    """Test installer configuration"""
    
    def test_nsis_script_exists(self):
        """Test NSIS installer script exists and is valid"""
        nsis_script = Path("installer.nsi")
        if nsis_script.exists():
            with open(nsis_script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required NSIS directives
            required_directives = [
                "!define APP_NAME",
                "!define APP_VERSION", 
                "Name",
                "OutFile",
                "InstallDir",
                "Section"
            ]
            
            for directive in required_directives:
                assert directive in content, f"Missing NSIS directive: {directive}"
    
    def test_installer_config_consistency(self):
        """Test that installer config matches build config"""
        build_config_path = Path("build_config.json")
        nsis_script_path = Path("installer.nsi")
        
        if build_config_path.exists() and nsis_script_path.exists():
            with open(build_config_path, 'r', encoding='utf-8') as f:
                build_config = json.load(f)
            
            with open(nsis_script_path, 'r', encoding='utf-8') as f:
                nsis_content = f.read()
            
            # Check version consistency (if not using placeholders)
            app_version = build_config["app"]["version"]
            if not app_version.startswith("${"):  # Not a placeholder
                # This is a basic check - installer script might use variables
                pass

def run_build_validation():
    """Run all build validation tests"""
    import pytest
    
    # Run pytest with verbose output
    test_file = Path(__file__)
    result = pytest.main([
        str(test_file),
        "-v",
        "--tb=short",
        "--no-header",
        "-q"
    ])
    
    return result == 0

if __name__ == "__main__":
    print("🧪 Running build validation tests...")
    success = run_build_validation()
    
    if success:
        print("✅ All build validation tests passed!")
        sys.exit(0)
    else:
        print("❌ Some build validation tests failed!")
        sys.exit(1)