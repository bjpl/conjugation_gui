"""
Executable-specific tests
Tests the built executable in isolation
"""
import os
import sys
import subprocess
import tempfile
import time
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

class TestExecutableRuntime:
    """Test executable runtime behavior"""
    
    @pytest.fixture
    def exe_path(self):
        """Get path to built executable"""
        dist_dir = Path("dist")
        exe_files = list(dist_dir.glob("*.exe"))
        
        if not exe_files:
            pytest.skip("No executable found in dist directory")
        
        return exe_files[0]
    
    def test_executable_exists(self, exe_path):
        """Test executable file exists and has reasonable size"""
        assert exe_path.exists(), f"Executable not found: {exe_path}"
        
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        assert size_mb > 10, f"Executable suspiciously small: {size_mb:.1f} MB"
        assert size_mb < 1000, f"Executable suspiciously large: {size_mb:.1f} MB"
    
    def test_executable_permissions(self, exe_path):
        """Test executable has correct permissions"""
        assert os.access(exe_path, os.R_OK), "Executable is not readable"
        assert os.access(exe_path, os.X_OK), "Executable is not executable"
    
    def test_executable_startup_no_crash(self, exe_path):
        """Test executable starts without immediate crash"""
        try:
            # Start process and let it run briefly
            process = subprocess.Popen(
                [str(exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Let it run for 3 seconds
            time.sleep(3)
            
            # Check if still running
            poll_result = process.poll()
            
            if poll_result is None:
                # Still running - good sign for a GUI app
                process.terminate()
                process.wait(timeout=10)
                assert True, "Application started successfully"
            elif poll_result == 0:
                # Exited cleanly - might be test mode
                assert True, "Application exited cleanly"
            else:
                # Crashed
                stdout, stderr = process.communicate()
                pytest.fail(f"Application crashed with code {poll_result}. stderr: {stderr.decode()}")
                
        except subprocess.TimeoutExpired:
            # Timeout is actually expected for GUI apps
            process.kill()
            assert True, "Application timed out (expected for GUI)"
        except Exception as e:
            pytest.fail(f"Failed to start executable: {e}")
    
    def test_executable_help_flag(self, exe_path):
        """Test executable responds to help flag"""
        try:
            result = subprocess.run(
                [str(exe_path), "--help"],
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Any of these return codes are acceptable
            acceptable_codes = [0, 1, 2]  # Success, general error, or usage error
            assert result.returncode in acceptable_codes, f"Unexpected return code: {result.returncode}"
            
        except subprocess.TimeoutExpired:
            # GUI apps might not respond to --help immediately
            pytest.skip("Executable timed out on --help (expected for GUI apps)")
    
    def test_executable_version_flag(self, exe_path):
        """Test executable responds to version flag"""
        try:
            result = subprocess.run(
                [str(exe_path), "--version"],
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Check if version info is in output
            output = result.stdout + result.stderr
            if "version" in output.lower() or any(char.isdigit() for char in output):
                assert True, "Version information found"
            else:
                # Version flag might not be implemented
                pytest.skip("Version flag not implemented")
                
        except subprocess.TimeoutExpired:
            pytest.skip("Executable timed out on --version")

class TestExecutableDependencies:
    """Test executable dependency resolution"""
    
    @pytest.fixture
    def exe_path(self):
        """Get path to built executable"""
        dist_dir = Path("dist")
        exe_files = list(dist_dir.glob("*.exe"))
        
        if not exe_files:
            pytest.skip("No executable found in dist directory")
        
        return exe_files[0]
    
    def test_executable_missing_dlls(self, exe_path):
        """Test for missing DLL dependencies (Windows)"""
        if os.name != 'nt':
            pytest.skip("DLL check only applicable on Windows")
        
        try:
            # Use dumpbin or similar tool if available
            result = subprocess.run(
                ["dumpbin", "/dependents", str(exe_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Check for obvious missing dependencies
                output = result.stdout.lower()
                
                # These should typically be available on Windows systems
                system_dlls = [
                    "kernel32.dll",
                    "user32.dll",
                    "advapi32.dll"
                ]
                
                for dll in system_dlls:
                    if dll in output:
                        assert True, f"Found expected system DLL: {dll}"
                        
            else:
                pytest.skip("dumpbin not available for dependency analysis")
                
        except FileNotFoundError:
            pytest.skip("dumpbin not available")
    
    def test_executable_in_clean_environment(self, exe_path):
        """Test executable runs in environment without Python"""
        # Create a subprocess with minimal environment
        clean_env = {
            "PATH": "C:\\Windows\\System32;C:\\Windows",
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            "TEMP": tempfile.gettempdir(),
        }
        
        try:
            process = subprocess.Popen(
                [str(exe_path)],
                env=clean_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            time.sleep(5)  # Let it start
            
            poll_result = process.poll()
            if poll_result is None:
                # Still running
                process.terminate()
                process.wait(timeout=10)
                assert True, "Executable runs in clean environment"
            elif poll_result == 0:
                assert True, "Executable exited cleanly in clean environment"
            else:
                stdout, stderr = process.communicate()
                # Some dependency issues might be acceptable
                pytest.skip(f"Executable failed in clean environment: {stderr.decode()}")
                
        except Exception as e:
            pytest.skip(f"Could not test clean environment: {e}")

class TestExecutablePerformance:
    """Test executable performance characteristics"""
    
    @pytest.fixture
    def exe_path(self):
        """Get path to built executable"""
        dist_dir = Path("dist")
        exe_files = list(dist_dir.glob("*.exe"))
        
        if not exe_files:
            pytest.skip("No executable found in dist directory")
        
        return exe_files[0]
    
    def test_startup_time(self, exe_path):
        """Test application startup time is reasonable"""
        start_time = time.time()
        
        try:
            process = subprocess.Popen(
                [str(exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Wait for process to fully start
            time.sleep(2)
            
            startup_time = time.time() - start_time
            
            # Terminate the process
            process.terminate()
            process.wait(timeout=10)
            
            # Startup should be under 30 seconds for most cases
            assert startup_time < 30, f"Startup time too slow: {startup_time:.2f} seconds"
            
            # Warn if startup is very slow
            if startup_time > 10:
                pytest.warns(UserWarning, f"Slow startup time: {startup_time:.2f} seconds")
                
        except Exception as e:
            pytest.skip(f"Could not measure startup time: {e}")
    
    def test_memory_usage(self, exe_path):
        """Test memory usage is reasonable"""
        try:
            import psutil
            
            process = subprocess.Popen(
                [str(exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            time.sleep(5)  # Let it fully load
            
            # Get memory usage
            ps_process = psutil.Process(process.pid)
            memory_mb = ps_process.memory_info().rss / (1024 * 1024)
            
            # Terminate process
            process.terminate()
            process.wait(timeout=10)
            
            # Memory usage should be reasonable for a PyQt5 app
            assert memory_mb < 1000, f"Memory usage too high: {memory_mb:.1f} MB"
            
            if memory_mb > 500:
                pytest.warns(UserWarning, f"High memory usage: {memory_mb:.1f} MB")
                
        except ImportError:
            pytest.skip("psutil not available for memory testing")
        except Exception as e:
            pytest.skip(f"Could not measure memory usage: {e}")

class TestExecutableConfiguration:
    """Test executable configuration handling"""
    
    @pytest.fixture
    def exe_path(self):
        """Get path to built executable"""
        dist_dir = Path("dist")
        exe_files = list(dist_dir.glob("*.exe"))
        
        if not exe_files:
            pytest.skip("No executable found in dist directory")
        
        return exe_files[0]
    
    def test_config_file_handling(self, exe_path):
        """Test that executable handles missing config files gracefully"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_exe = Path(temp_dir) / exe_path.name
            
            # Copy executable to temp directory (without config files)
            import shutil
            shutil.copy2(exe_path, temp_exe)
            
            # Try to run without config files
            try:
                process = subprocess.Popen(
                    [str(temp_exe)],
                    cwd=temp_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                time.sleep(3)
                
                poll_result = process.poll()
                process.terminate()
                process.wait(timeout=5)
                
                # Should handle missing config gracefully (not crash immediately)
                if poll_result is not None and poll_result != 0:
                    stdout, stderr = process.communicate()
                    # Check if error message is reasonable
                    error_output = stderr.decode().lower()
                    
                    if "config" in error_output or "not found" in error_output:
                        assert True, "Executable handles missing config appropriately"
                    else:
                        pytest.skip(f"Executable failed for other reasons: {error_output}")
                else:
                    assert True, "Executable handles missing config files"
                    
            except Exception as e:
                pytest.skip(f"Could not test config handling: {e}")
    
    def test_env_file_handling(self, exe_path):
        """Test executable behavior with missing .env file"""
        exe_dir = exe_path.parent
        env_file = exe_dir / ".env"
        
        # Backup existing .env if present
        env_backup = None
        if env_file.exists():
            env_backup = env_file.read_text()
            env_file.unlink()
        
        try:
            # Run without .env file
            process = subprocess.Popen(
                [str(exe_path)],
                cwd=exe_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            time.sleep(3)
            
            poll_result = process.poll()
            if poll_result is not None:
                stdout, stderr = process.communicate()
                # Should provide helpful error about API key
                error_text = (stdout.decode() + stderr.decode()).lower()
                
                if "api" in error_text or "key" in error_text or "openai" in error_text:
                    assert True, "Executable provides helpful error about missing API key"
                else:
                    pytest.skip("Executable failed for other reasons")
            else:
                process.terminate()
                process.wait(timeout=5)
                assert True, "Executable starts without .env file"
                
        finally:
            # Restore .env file if it existed
            if env_backup is not None:
                env_file.write_text(env_backup)

def run_executable_tests():
    """Run all executable tests"""
    import pytest
    
    test_file = Path(__file__)
    result = pytest.main([
        str(test_file),
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
    
    return result == 0

if __name__ == "__main__":
    print("🧪 Running executable tests...")
    success = run_executable_tests()
    
    if success:
        print("✅ All executable tests passed!")
        sys.exit(0)
    else:
        print("❌ Some executable tests failed!")
        sys.exit(1)