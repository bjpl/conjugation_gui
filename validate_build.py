"""
Comprehensive build validation script
Runs all validation checks before and after build
"""
import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Validation result structure"""
    name: str
    passed: bool
    message: str
    duration: float
    details: Optional[str] = None

class BuildValidator:
    """Comprehensive build validation"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.start_time = time.time()
    
    def run_validation(self, validation_func, name: str) -> ValidationResult:
        """Run a single validation with timing"""
        print(f"🔍 {name}...")
        start_time = time.time()
        
        try:
            passed, message, details = validation_func()
            duration = time.time() - start_time
            
            result = ValidationResult(name, passed, message, duration, details)
            status = "✅" if passed else "❌"
            print(f"   {status} {message} ({duration:.2f}s)")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = ValidationResult(name, False, f"Validation error: {e}", duration, str(e))
            print(f"   ❌ Validation error: {e} ({duration:.2f}s)")
            
            return result
    
    def validate_prerequisites(self) -> Tuple[bool, str, Optional[str]]:
        """Validate build prerequisites"""
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            issues.append(f"Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check main script
        if not Path("main.py").exists():
            issues.append("main.py not found")
        
        # Check configuration files
        config_files = ["build_config.json", "app_config.json"]
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    issues.append(f"Invalid JSON in {config_file}: {e}")
        
        # Check critical dependencies
        critical_deps = ["PyQt5", "openai", "requests", "dotenv"]
        missing_deps = []
        
        for dep in critical_deps:
            try:
                if dep == "dotenv":
                    import dotenv
                else:
                    __import__(dep)
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            issues.append(f"Missing dependencies: {', '.join(missing_deps)}")
        
        if issues:
            return False, f"Prerequisites failed: {'; '.join(issues)}", '\n'.join(issues)
        else:
            return True, "All prerequisites met", None
    
    def validate_pyinstaller_setup(self) -> Tuple[bool, str, Optional[str]]:
        """Validate PyInstaller setup"""
        try:
            import PyInstaller
            pyinstaller_version = PyInstaller.__version__
        except ImportError:
            return False, "PyInstaller not installed", "Install with: pip install pyinstaller"
        
        # Check spec files
        spec_files = ["SpanishConjugation.spec", "SpanishConjugation_Enhanced.spec"]
        valid_specs = []
        
        for spec_file in spec_files:
            if Path(spec_file).exists():
                try:
                    with open(spec_file, 'r', encoding='utf-8') as f:
                        spec_code = f.read()
                    compile(spec_code, spec_file, 'exec')
                    valid_specs.append(spec_file)
                except SyntaxError as e:
                    return False, f"Syntax error in {spec_file}", str(e)
        
        if not valid_specs:
            return False, "No valid spec files found", "Need .spec file for build"
        
        return True, f"PyInstaller {pyinstaller_version} with {len(valid_specs)} valid spec files", None
    
    def validate_hooks_and_imports(self) -> Tuple[bool, str, Optional[str]]:
        """Validate PyInstaller hooks and hidden imports"""
        hooks_dir = Path("pyinstaller_hooks")
        hook_count = 0
        issues = []
        
        if hooks_dir.exists():
            for hook_file in hooks_dir.glob("hook-*.py"):
                try:
                    with open(hook_file, 'r', encoding='utf-8') as f:
                        hook_code = f.read()
                    compile(hook_code, str(hook_file), 'exec')
                    hook_count += 1
                except SyntaxError as e:
                    issues.append(f"Syntax error in {hook_file.name}: {e}")
        
        # Test critical imports
        critical_imports = [
            "PyQt5.QtCore",
            "PyQt5.QtWidgets", 
            "PyQt5.QtGui",
            "openai",
            "requests",
            "json",
            "sqlite3",
        ]
        
        for imp in critical_imports:
            try:
                __import__(imp)
            except ImportError as e:
                issues.append(f"Cannot import {imp}: {e}")
        
        if issues:
            return False, f"Import/hook issues: {len(issues)} problems", '\n'.join(issues)
        else:
            return True, f"Hooks and imports valid ({hook_count} hooks)", None
    
    def validate_resources_and_assets(self) -> Tuple[bool, str, Optional[str]]:
        """Validate resources and assets"""
        issues = []
        resource_count = 0
        
        # Check data files
        data_files = [
            "app_config.json",
            ".env.example"
        ]
        
        for data_file in data_files:
            if Path(data_file).exists():
                if Path(data_file).stat().st_size > 0:
                    resource_count += 1
                else:
                    issues.append(f"{data_file} is empty")
            else:
                issues.append(f"{data_file} not found")
        
        # Check assets directory
        assets_dir = Path("assets")
        if assets_dir.exists():
            asset_files = list(assets_dir.glob("*"))
            resource_count += len(asset_files)
        
        # Check icon
        icon_candidates = ["assets/icon.ico", "icon.ico", "app.ico"]
        icon_found = any(Path(icon).exists() for icon in icon_candidates)
        
        if not icon_found:
            issues.append("No icon file found")
        
        if issues:
            return False, f"Resource issues: {len(issues)} problems", '\n'.join(issues)
        else:
            return True, f"Resources valid ({resource_count} files)", None
    
    def validate_build_scripts(self) -> Tuple[bool, str, Optional[str]]:
        """Validate build scripts"""
        scripts = {
            "build_exe.py": "Basic build script",
            "build_advanced.py": "Advanced build script",
            "build_installer.py": "Installer build script"
        }
        
        valid_scripts = []
        issues = []
        
        for script, description in scripts.items():
            if Path(script).exists():
                try:
                    # Try to import to check syntax
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("test_module", script)
                    module = importlib.util.module_from_spec(spec)
                    # Don't actually execute, just check if it can be loaded
                    valid_scripts.append(f"{script} ({description})")
                except Exception as e:
                    issues.append(f"Error in {script}: {e}")
        
        if not valid_scripts:
            return False, "No valid build scripts found", '\n'.join(issues)
        
        if issues:
            return False, f"Build script issues: {len(issues)} problems", '\n'.join(issues)
        else:
            return True, f"{len(valid_scripts)} build scripts valid", '\n'.join(valid_scripts)
    
    def validate_test_configuration(self) -> Tuple[bool, str, Optional[str]]:
        """Validate test configuration"""
        test_dir = Path("tests")
        test_count = 0
        
        if test_dir.exists():
            test_files = list(test_dir.glob("test_*.py"))
            test_count = len(test_files)
            
            # Check if pytest can be imported
            try:
                import pytest
                pytest_available = True
            except ImportError:
                pytest_available = False
        else:
            test_files = []
            pytest_available = False
        
        if test_count > 0 and pytest_available:
            return True, f"Tests configured ({test_count} test files, pytest available)", None
        elif test_count > 0:
            return False, f"Tests exist but pytest not available ({test_count} files)", "Install pytest"
        else:
            return True, "No tests configured (optional)", None
    
    def validate_executable_post_build(self) -> Tuple[bool, str, Optional[str]]:
        """Validate executable after build"""
        dist_dir = Path("dist")
        
        if not dist_dir.exists():
            return False, "No dist directory found", "Build may have failed"
        
        exe_files = list(dist_dir.glob("*.exe"))
        
        if not exe_files:
            return False, "No executable found in dist directory", "Check build output"
        
        exe_path = exe_files[0]
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        
        # Basic size validation
        if size_mb < 10:
            return False, f"Executable suspiciously small: {size_mb:.1f} MB", "May be missing dependencies"
        elif size_mb > 500:
            return False, f"Executable very large: {size_mb:.1f} MB", "May include unnecessary files"
        
        return True, f"Executable found: {exe_path.name} ({size_mb:.1f} MB)", None
    
    def validate_executable_startup(self) -> Tuple[bool, str, Optional[str]]:
        """Validate executable can start"""
        dist_dir = Path("dist")
        exe_files = list(dist_dir.glob("*.exe"))
        
        if not exe_files:
            return False, "No executable to test", "Run build first"
        
        exe_path = exe_files[0]
        
        try:
            # Try to start the executable
            process = subprocess.Popen(
                [str(exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Give it 5 seconds to start
            time.sleep(5)
            
            poll_result = process.poll()
            
            if poll_result is None:
                # Still running - good for GUI app
                process.terminate()
                process.wait(timeout=10)
                return True, "Executable starts successfully", None
            elif poll_result == 0:
                # Exited cleanly
                return True, "Executable runs and exits cleanly", None
            else:
                # Crashed
                stdout, stderr = process.communicate()
                error_msg = stderr.decode().strip()
                return False, f"Executable crashed (code {poll_result})", error_msg
                
        except Exception as e:
            return False, f"Failed to test executable startup: {e}", str(e)
    
    def run_pre_build_validation(self) -> bool:
        """Run all pre-build validations"""
        print("🔍 PRE-BUILD VALIDATION")
        print("=" * 50)
        
        validations = [
            (self.validate_prerequisites, "Prerequisites Check"),
            (self.validate_pyinstaller_setup, "PyInstaller Setup"),
            (self.validate_hooks_and_imports, "Hooks and Imports"),
            (self.validate_resources_and_assets, "Resources and Assets"),
            (self.validate_build_scripts, "Build Scripts"),
            (self.validate_test_configuration, "Test Configuration"),
        ]
        
        all_passed = True
        
        for validation_func, name in validations:
            result = self.run_validation(validation_func, name)
            self.results.append(result)
            if not result.passed:
                all_passed = False
        
        print(f"\n📊 Pre-build validation: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        return all_passed
    
    def run_post_build_validation(self) -> bool:
        """Run all post-build validations"""
        print("\n🔍 POST-BUILD VALIDATION")
        print("=" * 50)
        
        validations = [
            (self.validate_executable_post_build, "Executable Creation"),
            (self.validate_executable_startup, "Executable Startup"),
        ]
        
        all_passed = True
        
        for validation_func, name in validations:
            result = self.run_validation(validation_func, name)
            self.results.append(result)
            if not result.passed:
                all_passed = False
        
        print(f"\n📊 Post-build validation: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        return all_passed
    
    def generate_report(self) -> str:
        """Generate validation report"""
        total_time = time.time() - self.start_time
        passed_count = sum(1 for r in self.results if r.passed)
        failed_count = len(self.results) - passed_count
        
        report_lines = [
            "BUILD VALIDATION REPORT",
            "=" * 50,
            f"Total validations: {len(self.results)}",
            f"Passed: {passed_count}",
            f"Failed: {failed_count}",
            f"Total time: {total_time:.2f}s",
            "",
            "Detailed Results:",
            "-" * 30,
        ]
        
        for result in self.results:
            status = "✅" if result.passed else "❌"
            report_lines.append(f"{status} {result.name}: {result.message} ({result.duration:.2f}s)")
            
            if result.details:
                for line in result.details.split('\n'):
                    report_lines.append(f"   {line}")
        
        if failed_count > 0:
            report_lines.extend([
                "",
                "❌ VALIDATION FAILED",
                "Please fix the issues above before proceeding with the build."
            ])
        else:
            report_lines.extend([
                "",
                "✅ ALL VALIDATIONS PASSED",
                "Build should proceed successfully."
            ])
        
        return '\n'.join(report_lines)
    
    def save_report(self, filename: str = "validation_report.txt") -> None:
        """Save validation report to file"""
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 Validation report saved: {Path(filename).absolute()}")

def main():
    """Main validation entry point"""
    validator = BuildValidator()
    
    # Run pre-build validation
    pre_build_passed = validator.run_pre_build_validation()
    
    if not pre_build_passed:
        print("\n❌ Pre-build validation failed!")
        validator.save_report("pre_build_validation_report.txt")
        sys.exit(1)
    
    print("\n✅ Pre-build validation passed!")
    
    # Check if we should also run post-build validation
    if len(sys.argv) > 1 and sys.argv[1] == "--post-build":
        post_build_passed = validator.run_post_build_validation()
        
        if not post_build_passed:
            print("\n❌ Post-build validation failed!")
            validator.save_report("post_build_validation_report.txt")
            sys.exit(1)
        
        print("\n✅ Post-build validation passed!")
    
    # Generate final report
    validator.save_report()
    
    print("\n🎉 All validations completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())