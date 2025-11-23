"""
Advanced build script for Spanish Conjugation GUI
Includes version management, metadata handling, and comprehensive build process
"""
import os
import sys
import json
import shutil
import subprocess
import platform
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class BuildManager:
    """Advanced build manager for PyInstaller executable creation"""
    
    def __init__(self, config_file: str = "build_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        self.temp_dir = Path("temp_build")
        self.start_time = time.time()
        
    def load_config(self) -> Dict:
        """Load build configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file {self.config_file} not found!")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {self.config_file}: {e}")
            sys.exit(1)
    
    def check_requirements(self) -> bool:
        """Check if all build requirements are met"""
        print("🔍 Checking build requirements...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            print(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check main script
        if not os.path.exists("main.py"):
            print("❌ main.py not found!")
            return False
        print("✅ main.py found")
        
        # Check dependencies
        required_packages = ["PyInstaller", "PyQt5", "openai", "python-dotenv", "requests", "pillow"]
        missing_packages = []
        
        for package in required_packages:
            try:
                if package == "python-dotenv":
                    import dotenv
                elif package == "PyInstaller":
                    import PyInstaller
                elif package == "PyQt5":
                    import PyQt5
                elif package == "openai":
                    import openai
                elif package == "requests":
                    import requests
                elif package == "pillow":
                    import PIL
                print(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package}")
        
        if missing_packages:
            print(f"\n💡 Install missing packages with: pip install {' '.join(missing_packages)}")
            return False
        
        return True
    
    def get_version_info(self) -> Tuple[str, str, str]:
        """Get version information"""
        version = self.config['app']['version']
        build_number = datetime.now().strftime("%Y%m%d%H%M")
        full_version = f"{version}.{build_number}"
        
        return version, build_number, full_version
    
    def create_version_file(self) -> str:
        """Create version file for Windows executable"""
        version, build_number, full_version = self.get_version_info()
        app_config = self.config['app']
        
        # Convert version to tuple format (major, minor, patch, build)
        version_parts = version.split('.')
        while len(version_parts) < 4:
            version_parts.append('0')
        version_tuple = ', '.join(version_parts)
        
        version_content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_tuple}),
    prodvers=({version_tuple}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', '{app_config["author"]}'),
        StringStruct('FileDescription', '{app_config["description"]}'),
        StringStruct('FileVersion', '{full_version}'),
        StringStruct('InternalName', '{app_config["name"]}'),
        StringStruct('LegalCopyright', '{app_config["copyright"]}'),
        StringStruct('OriginalFilename', '{app_config["name"]}.exe'),
        StringStruct('ProductName', '{app_config["display_name"]}'),
        StringStruct('ProductVersion', '{version}'),
        StringStruct('BuildDate', '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'),
        StringStruct('BuildMachine', '{platform.node()}')
        ])
      ]), 
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
        
        version_file = "version_info.txt"
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(version_content)
        
        return version_file
    
    def prepare_build_environment(self) -> None:
        """Prepare the build environment"""
        print("🛠️ Preparing build environment...")
        
        # Clean previous builds if requested
        if self.config['build'].get('clean', True):
            for directory in [self.build_dir, self.dist_dir, self.temp_dir]:
                if directory.exists():
                    shutil.rmtree(directory)
                    print(f"🧹 Cleaned {directory}")
        
        # Create necessary directories
        for directory in [self.build_dir, self.dist_dir, "assets"]:
            Path(directory).mkdir(exist_ok=True)
        
        # Create default icon if none exists
        if not os.path.exists(self.config['resources']['icon']):
            self.create_default_icon()
    
    def create_default_icon(self) -> None:
        """Create a default icon using PIL"""
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple icon
            size = (64, 64)
            icon = Image.new('RGBA', size, (70, 130, 180, 255))  # Steel blue
            draw = ImageDraw.Draw(icon)
            
            # Draw a simple "S" for Spanish
            draw.text((20, 15), "S", fill=(255, 255, 255, 255))
            
            icon_path = Path(self.config['resources']['icon'])
            icon_path.parent.mkdir(exist_ok=True)
            icon.save(icon_path, format='ICO')
            
            print(f"🎨 Created default icon: {icon_path}")
        except ImportError:
            print("⚠️ PIL not available, skipping icon creation")
        except Exception as e:
            print(f"⚠️ Could not create icon: {e}")
    
    def build_executable(self) -> bool:
        """Build the executable using PyInstaller"""
        print("🔨 Building executable...")
        
        version_file = self.create_version_file()
        app_config = self.config['app']
        build_config = self.config['build']
        
        # Construct PyInstaller command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--name", app_config['name'],
            "--specpath", str(self.build_dir),
            "--workpath", str(self.build_dir / "work"),
            "--distpath", str(self.dist_dir),
        ]
        
        # Build mode
        if build_config.get('one_file', True):
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")
        
        # Console mode
        if not build_config.get('console', False):
            cmd.append("--windowed")
        
        # Debug mode
        if build_config.get('debug', False):
            cmd.append("--debug=all")
        
        # UPX compression
        if build_config.get('upx', True):
            cmd.append("--upx-dir=upx")  # Assuming UPX is in PATH or upx folder
        else:
            cmd.append("--noupx")
        
        # Icon
        icon_path = self.config['resources']['icon']
        if os.path.exists(icon_path):
            cmd.extend(["--icon", icon_path])
        
        # Version info
        if os.path.exists(version_file):
            cmd.extend(["--version-file", version_file])
        
        # Add data files
        for data_file in self.config['resources']['data_files']:
            source = data_file['source']
            dest = data_file['destination']
            if os.path.exists(source):
                cmd.extend(["--add-data", f"{source}{os.pathsep}{dest}"])
        
        # Hidden imports
        essential_imports = [
            "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets",
            "openai", "dotenv", "requests", "PIL"
        ]
        for imp in essential_imports:
            cmd.extend(["--hidden-import", imp])
        
        # Exclude modules
        for module in self.config['resources'].get('exclude_modules', []):
            cmd.extend(["--exclude-module", module])
        
        # Hook directories
        if os.path.exists("pyinstaller_hooks"):
            cmd.extend(["--additional-hooks-dir", "pyinstaller_hooks"])
        
        # Runtime hooks
        if os.path.exists("runtime_hooks.py"):
            cmd.extend(["--runtime-hook", "runtime_hooks.py"])
        
        # Main script
        cmd.append("main.py")
        
        print("🚀 PyInstaller command:")
        print(" ".join(cmd))
        print("\nThis may take several minutes...\n")
        
        try:
            # Run PyInstaller
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Build completed successfully!")
                return True
            else:
                print(f"❌ Build failed with return code: {result.returncode}")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False
        except FileNotFoundError:
            print("❌ PyInstaller not found! Install with: pip install pyinstaller")
            return False
        
        finally:
            # Cleanup version file
            if os.path.exists(version_file):
                os.remove(version_file)
    
    def validate_executable(self) -> bool:
        """Validate the built executable"""
        print("🔍 Validating executable...")
        
        app_name = self.config['app']['name']
        if self.config['build'].get('one_file', True):
            exe_path = self.dist_dir / f"{app_name}.exe"
        else:
            exe_path = self.dist_dir / app_name / f"{app_name}.exe"
        
        if not exe_path.exists():
            print(f"❌ Executable not found: {exe_path}")
            return False
        
        # Check file size
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"📦 Executable size: {size_mb:.1f} MB")
        
        if size_mb < 10:
            print("⚠️ Warning: Executable seems unusually small")
        elif size_mb > 500:
            print("⚠️ Warning: Executable is very large")
        
        # Try to get version info (Windows only)
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ["powershell", "-Command", f"(Get-ItemProperty '{exe_path}').VersionInfo.FileVersion"],
                    capture_output=True, text=True, check=True
                )
                version_info = result.stdout.strip()
                if version_info:
                    print(f"📋 Executable version: {version_info}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        print(f"✅ Executable validated: {exe_path.absolute()}")
        return True
    
    def create_distribution(self) -> bool:
        """Create distribution package"""
        print("📦 Creating distribution package...")
        
        app_name = self.config['app']['name']
        version = self.config['app']['version']
        dist_name = f"{app_name}_v{version}_Windows"
        dist_path = Path(dist_name)
        
        # Clean existing distribution
        if dist_path.exists():
            shutil.rmtree(dist_path)
        
        dist_path.mkdir()
        
        # Copy executable
        if self.config['build'].get('one_file', True):
            exe_source = self.dist_dir / f"{app_name}.exe"
        else:
            exe_source = self.dist_dir / app_name
        
        if exe_source.is_file():
            shutil.copy2(exe_source, dist_path)
        else:
            shutil.copytree(exe_source, dist_path / app_name)
        
        # Copy additional files
        additional_files = [
            ".env.example",
            "README.md",
            "LICENSE"
        ]
        
        for file in additional_files:
            if os.path.exists(file):
                shutil.copy2(file, dist_path)
        
        # Create startup batch file
        batch_content = f"""@echo off
title {self.config['app']['display_name']}
echo Starting {self.config['app']['display_name']}...
echo.

REM Check for .env file
if not exist .env (
    echo ⚠️  SETUP REQUIRED ⚠️
    echo.
    echo Please create a .env file with your OpenAI API key:
    echo 1. Copy .env.example to .env
    echo 2. Edit .env and add your API key
    echo 3. Get API key from: https://platform.openai.com/api-keys
    echo.
    pause
    exit /b 1
)

REM Launch application
{app_name}.exe

REM Pause on error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code: %errorlevel%
    pause
)
"""
        
        with open(dist_path / "Launch.bat", "w", encoding='utf-8') as f:
            f.write(batch_content)
        
        # Create installation guide
        install_guide = f"""# {self.config['app']['display_name']} - Installation Guide

## Quick Start

1. **Get OpenAI API Key**
   - Visit: https://platform.openai.com/api-keys
   - Create a new API key
   - Copy the key (starts with sk-...)

2. **Configure Application**
   - Rename `.env.example` to `.env`
   - Open `.env` in a text editor
   - Replace `your_openai_api_key_here` with your actual API key
   - Save the file

3. **Launch Application**
   - Double-click `Launch.bat` for guided startup
   - Or run `{app_name}.exe` directly

## Features

- Interactive Spanish conjugation practice
- AI-powered feedback and explanations
- Multiple practice modes (grammar, tasks, speed)
- Progress tracking and statistics
- Offline mode available

## System Requirements

- Windows 10 or later (64-bit)
- Internet connection for AI features
- OpenAI API key (paid service)

## Troubleshooting

### Application won't start
- Ensure `.env` file exists with valid API key
- Check Windows Defender/antivirus settings
- Run as administrator if needed

### API errors
- Verify API key is correct and active
- Check OpenAI account billing/credits
- Ensure internet connection is stable

### Performance issues
- Close other applications to free memory
- Try offline mode for local practice
- Check system meets minimum requirements

## Support

- Version: {version}
- Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Homepage: {self.config['app'].get('homepage', 'N/A')}

For support, please check the project homepage or contact the developer.
"""
        
        with open(dist_path / "INSTALL.md", "w", encoding='utf-8') as f:
            f.write(install_guide)
        
        print(f"✅ Distribution created: {dist_path.absolute()}")
        
        # Create ZIP archive
        try:
            import zipfile
            
            zip_path = f"{dist_name}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(dist_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, dist_path.parent)
                        zipf.write(file_path, arc_path)
            
            print(f"📦 Distribution archive: {zip_path}")
            
        except ImportError:
            print("⚠️ Could not create ZIP archive (zipfile module not available)")
        
        return True
    
    def build_summary(self) -> None:
        """Print build summary"""
        build_time = time.time() - self.start_time
        version, build_number, full_version = self.get_version_info()
        
        print("\n" + "="*60)
        print("🎉 BUILD COMPLETE!")
        print("="*60)
        print(f"Application: {self.config['app']['display_name']}")
        print(f"Version: {full_version}")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Build time: {build_time:.1f} seconds")
        print(f"Build date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # File information
        app_name = self.config['app']['name']
        if self.config['build'].get('one_file', True):
            exe_path = self.dist_dir / f"{app_name}.exe"
        else:
            exe_path = self.dist_dir / app_name / f"{app_name}.exe"
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Executable: {exe_path.absolute()} ({size_mb:.1f} MB)")
        
        print("\n📋 Next Steps:")
        print("1. Test the executable on a clean Windows system")
        print("2. Create installer using NSIS (optional)")
        print("3. Set up code signing for security (recommended)")
        print("4. Distribute to users with installation guide")
        print("="*60)
    
    def run_build(self) -> bool:
        """Run the complete build process"""
        print(f"🚀 Starting build for {self.config['app']['display_name']} v{self.config['app']['version']}")
        print(f"🕐 Build started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        # Check requirements
        if not self.check_requirements():
            return False
        
        # Prepare environment
        self.prepare_build_environment()
        
        # Build executable
        if not self.build_executable():
            return False
        
        # Validate result
        if not self.validate_executable():
            return False
        
        # Create distribution
        if not self.create_distribution():
            return False
        
        # Show summary
        self.build_summary()
        
        return True

def main():
    """Main entry point"""
    builder = BuildManager()
    
    try:
        success = builder.run_build()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()