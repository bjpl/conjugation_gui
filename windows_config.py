"""
Windows-specific configurations and utilities
"""
import os
import sys
import winreg
import platform
from pathlib import Path
from typing import Dict, List, Optional

class WindowsConfig:
    """Windows-specific configuration manager"""
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """Get Windows system information"""
        try:
            info = {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            }
            
            # Windows version details
            if sys.platform == 'win32':
                import winver
                info.update({
                    'windows_version': winver.get_winver(),
                    'build_number': winver.get_build_number(),
                })
        except ImportError:
            pass
            
        return info
    
    @staticmethod
    def check_vcredist() -> bool:
        """Check if Visual C++ Redistributable is installed"""
        try:
            # Check registry for VC++ Redistributable
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64") as key:
                installed, _ = winreg.QueryValueEx(key, "Installed")
                return installed == 1
        except (FileNotFoundError, OSError, winreg.error):
            return False
    
    @staticmethod
    def get_temp_dir() -> Path:
        """Get appropriate temporary directory"""
        temp_dirs = [
            os.environ.get('TEMP'),
            os.environ.get('TMP'),
            r'C:\Windows\Temp',
            r'C:\Temp'
        ]
        
        for temp_dir in temp_dirs:
            if temp_dir and Path(temp_dir).exists():
                return Path(temp_dir)
        
        # Fallback
        return Path.cwd() / 'temp'
    
    @staticmethod
    def get_app_data_dir(app_name: str) -> Path:
        """Get application data directory"""
        app_data = os.environ.get('APPDATA')
        if app_data:
            return Path(app_data) / app_name
        else:
            return Path.home() / 'AppData' / 'Roaming' / app_name
    
    @staticmethod
    def create_shortcut(exe_path: Path, shortcut_path: Path, 
                       description: str = "", icon_path: Optional[Path] = None) -> bool:
        """Create Windows shortcut"""
        try:
            import win32com.client
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(exe_path)
            shortcut.WorkingDirectory = str(exe_path.parent)
            shortcut.Description = description
            
            if icon_path and icon_path.exists():
                shortcut.IconLocation = str(icon_path)
            
            shortcut.save()
            return True
            
        except ImportError:
            print("⚠️ win32com not available, cannot create shortcuts")
            return False
        except Exception as e:
            print(f"⚠️ Error creating shortcut: {e}")
            return False
    
    @staticmethod
    def add_to_startup(app_name: str, exe_path: Path) -> bool:
        """Add application to Windows startup"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, str(exe_path))
            return True
        except (OSError, winreg.error) as e:
            print(f"⚠️ Error adding to startup: {e}")
            return False
    
    @staticmethod
    def remove_from_startup(app_name: str) -> bool:
        """Remove application from Windows startup"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_WRITE) as key:
                winreg.DeleteValue(key, app_name)
            return True
        except (OSError, winreg.error, FileNotFoundError) as e:
            print(f"⚠️ Error removing from startup: {e}")
            return False
    
    @staticmethod
    def check_windows_defender() -> Dict[str, bool]:
        """Check Windows Defender status and exclusions"""
        results = {
            'defender_enabled': False,
            'real_time_protection': False,
            'exclusions_needed': False
        }
        
        try:
            import subprocess
            
            # Check if Windows Defender is running
            result = subprocess.run([
                'powershell', '-Command',
                'Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                results['defender_enabled'] = 'True' in output
                results['real_time_protection'] = 'True' in output
                results['exclusions_needed'] = results['real_time_protection']
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Assume defender is running if we can't check
            results['exclusions_needed'] = True
        
        return results
    
    @staticmethod
    def suggest_defender_exclusion(exe_path: Path) -> List[str]:
        """Suggest Windows Defender exclusion commands"""
        commands = [
            f'powershell -Command "Add-MpPreference -ExclusionPath \'{exe_path}\'"',
            f'powershell -Command "Add-MpPreference -ExclusionPath \'{exe_path.parent}\'"',
        ]
        
        return commands

class WindowsInstaller:
    """Windows installer utilities"""
    
    @staticmethod
    def create_uninstall_registry_entry(app_info: Dict[str, str], exe_path: Path) -> bool:
        """Create uninstall registry entry"""
        try:
            uninstall_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            app_key = f"{uninstall_key}\\{app_info['name']}"
            
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, app_key) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, app_info['display_name'])
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, app_info['version'])
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, app_info['author'])
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(exe_path.parent))
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, 
                                 f'"{exe_path.parent / "uninstall.exe"}"')
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            
            return True
            
        except (OSError, winreg.error) as e:
            print(f"⚠️ Error creating uninstall entry: {e}")
            return False
    
    @staticmethod
    def remove_uninstall_registry_entry(app_name: str) -> bool:
        """Remove uninstall registry entry"""
        try:
            uninstall_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, f"{uninstall_key}\\{app_name}")
            return True
        except (OSError, winreg.error, FileNotFoundError) as e:
            print(f"⚠️ Error removing uninstall entry: {e}")
            return False

def check_compatibility() -> Dict[str, bool]:
    """Check Windows compatibility"""
    results = {
        'supported_os': False,
        'vcredist_available': False,
        'python_compatible': False,
        'permissions_ok': False
    }
    
    # Check OS version
    if sys.platform == 'win32':
        version = platform.version().split('.')
        major_version = int(version[0])
        build_number = int(version[2]) if len(version) > 2 else 0
        
        # Windows 10 (build 10240+) or Windows 11
        if major_version >= 10 and build_number >= 10240:
            results['supported_os'] = True
    
    # Check VC++ Redistributable
    results['vcredist_available'] = WindowsConfig.check_vcredist()
    
    # Check Python version
    if sys.version_info >= (3, 8):
        results['python_compatible'] = True
    
    # Check write permissions
    try:
        test_file = Path.cwd() / 'test_permissions.tmp'
        test_file.write_text('test')
        test_file.unlink()
        results['permissions_ok'] = True
    except (OSError, PermissionError):
        results['permissions_ok'] = False
    
    return results

if __name__ == "__main__":
    """Test Windows configuration"""
    print("Windows Configuration Test")
    print("=" * 30)
    
    # System info
    info = WindowsConfig.get_system_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print("\nCompatibility Check:")
    compat = check_compatibility()
    for key, value in compat.items():
        status = "✅" if value else "❌"
        print(f"{key}: {status}")
    
    # Windows Defender check
    print("\nWindows Defender:")
    defender = WindowsConfig.check_windows_defender()
    for key, value in defender.items():
        status = "✅" if value else "❌"
        print(f"{key}: {status}")