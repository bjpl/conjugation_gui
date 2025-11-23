"""
Comprehensive compatibility and system checks for Windows systems
Ensures the application can run on clean Windows installations
"""
import os
import sys
import platform
import subprocess
import winreg
import json
import ctypes
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class SystemInfo:
    """System information structure"""
    os_name: str
    os_version: str
    os_build: str
    architecture: str
    python_version: str
    is_64bit: bool
    total_memory: int
    available_disk: int
    
@dataclass
class CompatibilityResult:
    """Compatibility check result"""
    name: str
    passed: bool
    message: str
    severity: str  # 'critical', 'warning', 'info'
    fix_suggestion: Optional[str] = None

class SystemChecker:
    """Comprehensive system compatibility checker"""
    
    def __init__(self):
        self.results: List[CompatibilityResult] = []
        self.system_info = self.get_system_info()
    
    def get_system_info(self) -> SystemInfo:
        """Gather comprehensive system information"""
        try:
            # Memory information
            kernel32 = ctypes.windll.kernel32
            memory_status = ctypes.Structure()
            memory_status._fields_ = [
                ('dwLength', ctypes.c_ulong),
                ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong),
                ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong),
                ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong),
                ('ullAvailVirtual', ctypes.c_ulonglong),
            ]
            memory_status.dwLength = ctypes.sizeof(memory_status)
            kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
            total_memory = memory_status.ullTotalPhys // (1024**3)  # GB
        except:
            total_memory = 0
        
        # Disk space
        try:
            disk_usage = os.statvfs('C:\\') if hasattr(os, 'statvfs') else None
            if disk_usage:
                available_disk = (disk_usage.f_bavail * disk_usage.f_frsize) // (1024**3)
            else:
                # Alternative method for Windows
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p('C:\\'),
                    ctypes.pointer(free_bytes),
                    None,
                    None
                )
                available_disk = free_bytes.value // (1024**3)
        except:
            available_disk = 0
        
        return SystemInfo(
            os_name=platform.system(),
            os_version=platform.release(),
            os_build=platform.version(),
            architecture=platform.machine(),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            is_64bit=platform.architecture()[0] == '64bit',
            total_memory=total_memory,
            available_disk=available_disk
        )
    
    def check_windows_version(self) -> CompatibilityResult:
        """Check Windows version compatibility"""
        try:
            version = platform.version().split('.')
            major_version = int(version[0])
            build_number = int(version[2]) if len(version) > 2 else 0
            
            # Windows 10 minimum (build 10240)
            if major_version >= 10 and build_number >= 10240:
                return CompatibilityResult(
                    "Windows Version",
                    True,
                    f"Windows {platform.release()} (Build {build_number}) - Compatible",
                    "info"
                )
            elif major_version == 10 and build_number < 10240:
                return CompatibilityResult(
                    "Windows Version",
                    False,
                    f"Windows 10 build {build_number} is too old. Minimum build 10240 required.",
                    "critical",
                    "Please update Windows 10 to the latest version"
                )
            else:
                return CompatibilityResult(
                    "Windows Version",
                    False,
                    f"Windows {platform.release()} is not supported. Windows 10+ required.",
                    "critical",
                    "Please upgrade to Windows 10 or Windows 11"
                )
        except Exception as e:
            return CompatibilityResult(
                "Windows Version",
                False,
                f"Could not determine Windows version: {e}",
                "critical"
            )
    
    def check_architecture(self) -> CompatibilityResult:
        """Check system architecture"""
        if self.system_info.is_64bit:
            return CompatibilityResult(
                "System Architecture",
                True,
                f"64-bit system detected ({self.system_info.architecture})",
                "info"
            )
        else:
            return CompatibilityResult(
                "System Architecture",
                False,
                f"32-bit system detected. 64-bit system required.",
                "critical",
                "Please use a 64-bit Windows system"
            )
    
    def check_memory(self) -> CompatibilityResult:
        """Check system memory"""
        if self.system_info.total_memory >= 4:
            return CompatibilityResult(
                "System Memory",
                True,
                f"{self.system_info.total_memory} GB RAM available",
                "info"
            )
        elif self.system_info.total_memory >= 2:
            return CompatibilityResult(
                "System Memory",
                True,
                f"{self.system_info.total_memory} GB RAM - may experience slow performance",
                "warning",
                "Consider upgrading to 4GB+ RAM for better performance"
            )
        else:
            return CompatibilityResult(
                "System Memory",
                False,
                f"Only {self.system_info.total_memory} GB RAM detected. Minimum 2GB required.",
                "critical",
                "Please upgrade system memory to at least 2GB"
            )
    
    def check_disk_space(self) -> CompatibilityResult:
        """Check available disk space"""
        if self.system_info.available_disk >= 1:
            return CompatibilityResult(
                "Disk Space",
                True,
                f"{self.system_info.available_disk} GB free space available",
                "info"
            )
        elif self.system_info.available_disk >= 0.5:
            return CompatibilityResult(
                "Disk Space",
                True,
                f"Only {self.system_info.available_disk} GB free space - may need cleanup",
                "warning",
                "Consider freeing up disk space for better performance"
            )
        else:
            return CompatibilityResult(
                "Disk Space",
                False,
                f"Insufficient disk space: {self.system_info.available_disk} GB free",
                "critical",
                "Please free up at least 500MB of disk space"
            )
    
    def check_vcredist(self) -> CompatibilityResult:
        """Check Visual C++ Redistributable"""
        try:
            # Check for VC++ Redistributable 2015-2022
            keys_to_check = [
                r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
                r"SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
            ]
            
            for key_path in keys_to_check:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                        installed, _ = winreg.QueryValueEx(key, "Installed")
                        if installed == 1:
                            version, _ = winreg.QueryValueEx(key, "Version")
                            return CompatibilityResult(
                                "Visual C++ Redistributable",
                                True,
                                f"VC++ Redistributable found (version {version})",
                                "info"
                            )
                except (FileNotFoundError, OSError):
                    continue
            
            return CompatibilityResult(
                "Visual C++ Redistributable",
                False,
                "Visual C++ Redistributable 2015-2022 not found",
                "critical",
                "Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe"
            )
            
        except Exception as e:
            return CompatibilityResult(
                "Visual C++ Redistributable",
                False,
                f"Could not check VC++ Redistributable: {e}",
                "warning",
                "Manual check recommended"
            )
    
    def check_dotnet(self) -> CompatibilityResult:
        """Check .NET Framework (if needed)"""
        try:
            # Check .NET Framework 4.8+
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full") as key:
                release, _ = winreg.QueryValueEx(key, "Release")
                
                if release >= 528040:  # .NET Framework 4.8
                    return CompatibilityResult(
                        ".NET Framework",
                        True,
                        f".NET Framework 4.8+ detected (release {release})",
                        "info"
                    )
                else:
                    return CompatibilityResult(
                        ".NET Framework",
                        True,
                        f".NET Framework version may be outdated (release {release})",
                        "warning",
                        "Consider updating to .NET Framework 4.8"
                    )
        except (FileNotFoundError, OSError):
            return CompatibilityResult(
                ".NET Framework",
                True,
                ".NET Framework check skipped (not required for PyQt5 app)",
                "info"
            )
    
    def check_antivirus(self) -> CompatibilityResult:
        """Check for antivirus that might interfere"""
        try:
            # Check Windows Defender status
            result = subprocess.run([
                'powershell', '-Command',
                'Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if 'True' in output:
                    return CompatibilityResult(
                        "Antivirus Status",
                        True,
                        "Windows Defender active - may need exclusions",
                        "warning",
                        "Add application folder to Windows Defender exclusions if needed"
                    )
                else:
                    return CompatibilityResult(
                        "Antivirus Status",
                        True,
                        "Real-time protection disabled or third-party antivirus",
                        "info"
                    )
            else:
                return CompatibilityResult(
                    "Antivirus Status",
                    True,
                    "Could not determine antivirus status",
                    "info"
                )
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return CompatibilityResult(
                "Antivirus Status",
                True,
                "Antivirus check skipped",
                "info"
            )
    
    def check_internet_connectivity(self) -> CompatibilityResult:
        """Check internet connectivity for OpenAI API"""
        try:
            import urllib.request
            urllib.request.urlopen('https://api.openai.com', timeout=10)
            return CompatibilityResult(
                "Internet Connectivity",
                True,
                "Internet connection to OpenAI API verified",
                "info"
            )
        except Exception as e:
            return CompatibilityResult(
                "Internet Connectivity",
                False,
                f"Cannot reach OpenAI API: {e}",
                "warning",
                "Check internet connection and firewall settings"
            )
    
    def check_ssl_certificates(self) -> CompatibilityResult:
        """Check SSL certificate configuration"""
        try:
            import ssl
            import certifi
            
            # Verify SSL context can be created
            context = ssl.create_default_context()
            
            # Check certificate bundle
            cert_path = certifi.where()
            if os.path.exists(cert_path):
                return CompatibilityResult(
                    "SSL Certificates",
                    True,
                    f"SSL certificates available: {cert_path}",
                    "info"
                )
            else:
                return CompatibilityResult(
                    "SSL Certificates",
                    False,
                    "SSL certificate bundle not found",
                    "critical",
                    "Reinstall certifi package: pip install --upgrade certifi"
                )
                
        except Exception as e:
            return CompatibilityResult(
                "SSL Certificates",
                False,
                f"SSL configuration error: {e}",
                "critical",
                "Check Python SSL installation"
            )
    
    def check_permissions(self) -> CompatibilityResult:
        """Check file system permissions"""
        try:
            # Test write permissions in current directory
            test_file = Path.cwd() / 'permission_test.tmp'
            test_file.write_text('test')
            test_file.unlink()
            
            # Test temp directory access
            temp_dir = Path(os.environ.get('TEMP', 'C:\\Windows\\Temp'))
            temp_test = temp_dir / 'permission_test.tmp'
            temp_test.write_text('test')
            temp_test.unlink()
            
            return CompatibilityResult(
                "File Permissions",
                True,
                "Read/write permissions verified",
                "info"
            )
            
        except (OSError, PermissionError) as e:
            return CompatibilityResult(
                "File Permissions",
                False,
                f"Permission denied: {e}",
                "critical",
                "Run as administrator or check folder permissions"
            )
    
    def check_python_modules(self) -> CompatibilityResult:
        """Check required Python modules"""
        required_modules = {
            'PyQt5': 'PyQt5',
            'openai': 'openai',
            'requests': 'requests', 
            'dotenv': 'python-dotenv',
            'PIL': 'pillow',
            'ssl': 'built-in',
            'json': 'built-in',
            'sqlite3': 'built-in'
        }
        
        missing_modules = []
        for module, package in required_modules.items():
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(package)
        
        if not missing_modules:
            return CompatibilityResult(
                "Python Modules",
                True,
                "All required Python modules available",
                "info"
            )
        else:
            return CompatibilityResult(
                "Python Modules",
                False,
                f"Missing modules: {', '.join(missing_modules)}",
                "critical",
                f"Install missing modules: pip install {' '.join(missing_modules)}"
            )
    
    def run_all_checks(self) -> List[CompatibilityResult]:
        """Run all compatibility checks"""
        checks = [
            self.check_windows_version,
            self.check_architecture,
            self.check_memory,
            self.check_disk_space,
            self.check_vcredist,
            self.check_dotnet,
            self.check_antivirus,
            self.check_internet_connectivity,
            self.check_ssl_certificates,
            self.check_permissions,
            self.check_python_modules,
        ]
        
        self.results = []
        for check in checks:
            try:
                result = check()
                self.results.append(result)
            except Exception as e:
                self.results.append(CompatibilityResult(
                    check.__name__.replace('check_', '').replace('_', ' ').title(),
                    False,
                    f"Check failed: {e}",
                    "warning"
                ))
        
        return self.results
    
    def generate_report(self, save_to_file: bool = True) -> str:
        """Generate compatibility report"""
        report_lines = [
            "SYSTEM COMPATIBILITY REPORT",
            "=" * 50,
            "",
            "System Information:",
            f"  OS: {self.system_info.os_name} {self.system_info.os_version}",
            f"  Build: {self.system_info.os_build}",
            f"  Architecture: {self.system_info.architecture}",
            f"  Python: {self.system_info.python_version}",
            f"  Memory: {self.system_info.total_memory} GB",
            f"  Disk Space: {self.system_info.available_disk} GB free",
            "",
            "Compatibility Checks:",
            "-" * 30,
        ]
        
        critical_issues = []
        warnings = []
        
        for result in self.results:
            status = "✅" if result.passed else "❌"
            if result.severity == "warning" and result.passed:
                status = "⚠️"
            
            report_lines.append(f"{status} {result.name}: {result.message}")
            
            if result.fix_suggestion:
                report_lines.append(f"   💡 {result.fix_suggestion}")
            
            if not result.passed and result.severity == "critical":
                critical_issues.append(result)
            elif result.severity == "warning":
                warnings.append(result)
        
        report_lines.extend(["", "Summary:", "-" * 20])
        
        if critical_issues:
            report_lines.append(f"❌ {len(critical_issues)} critical issues found")
            report_lines.append("   Application may not work properly until resolved")
        
        if warnings:
            report_lines.append(f"⚠️ {len(warnings)} warnings")
            report_lines.append("   Application should work but may have issues")
        
        if not critical_issues and not warnings:
            report_lines.append("✅ System appears fully compatible")
        
        report = "\n".join(report_lines)
        
        if save_to_file:
            with open("compatibility_report.txt", "w", encoding="utf-8") as f:
                f.write(report)
        
        return report

def main():
    """Run compatibility check"""
    print("🔍 Running comprehensive system compatibility check...")
    print("=" * 60)
    
    checker = SystemChecker()
    results = checker.run_all_checks()
    
    # Print results
    critical_count = sum(1 for r in results if not r.passed and r.severity == "critical")
    warning_count = sum(1 for r in results if r.severity == "warning")
    
    print(f"\n📊 Check Results: {len(results)} checks performed")
    print(f"❌ Critical issues: {critical_count}")
    print(f"⚠️ Warnings: {warning_count}")
    print(f"✅ Passed: {len(results) - critical_count - warning_count}")
    
    # Generate and display report
    report = checker.generate_report()
    print("\n" + report)
    
    print(f"\n📄 Report saved to: {Path('compatibility_report.txt').absolute()}")
    
    # Return appropriate exit code
    if critical_count > 0:
        print("\n❌ Critical issues found. Please resolve before running the application.")
        return 1
    elif warning_count > 0:
        print("\n⚠️ Warnings found. Application should work but may have issues.")
        return 0
    else:
        print("\n✅ System fully compatible!")
        return 0

if __name__ == "__main__":
    sys.exit(main())