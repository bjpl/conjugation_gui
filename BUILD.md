# Build Guide - Spanish Conjugation Practice

This guide provides comprehensive instructions for building Windows executables and installers for the Spanish Conjugation Practice application.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Build Methods](#build-methods)
- [Configuration](#configuration)
- [Advanced Build Options](#advanced-build-options)
- [Creating Installers](#creating-installers)
- [CI/CD Pipeline](#cicd-pipeline)
- [Troubleshooting](#troubleshooting)
- [Distribution](#distribution)

## 🚀 Quick Start

For a quick build with default settings:

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 2. Run basic build
python build_exe.py
```

For production builds:

```bash
# 1. Validate system compatibility
python compatibility_check.py

# 2. Run pre-build validation
python validate_build.py

# 3. Build executable with advanced options
python build_advanced.py

# 4. Create installer (requires NSIS)
python build_installer.py

# 5. Run post-build validation
python validate_build.py --post-build
```

## 📦 Prerequisites

### System Requirements

- **Windows 10 or later (64-bit)**
- **Python 3.8+** (3.11 recommended)
- **4GB RAM** (minimum 2GB)
- **2GB free disk space**
- **Internet connection** (for downloading dependencies)

### Required Software

#### Python Dependencies
```bash
pip install pyinstaller
pip install PyQt5==5.15.7
pip install PyQtWebEngine==5.15.7
pip install python-dotenv>=1.0.0
pip install openai>=1.0.0
pip install requests>=2.32.0
pip install pillow==10.0.0
```

#### Optional Tools
- **NSIS 3.x** - For creating installers
  - Download: https://nsis.sourceforge.io/Download
  - Or install via chocolatey: `choco install nsis`
- **UPX** - For executable compression (optional)
- **Git** - For version control and CI/CD

### System Validation

Run the compatibility checker before building:

```bash
python compatibility_check.py
```

This checks:
- Windows version and architecture
- System memory and disk space
- Visual C++ Redistributable
- Internet connectivity to OpenAI
- SSL certificates
- File system permissions

## 🔨 Build Methods

### Method 1: Simple Build (build_exe.py)

Best for: Quick testing and development

```bash
python build_exe.py
```

**Features:**
- Uses existing PyInstaller spec file
- Creates basic distribution folder
- Minimal configuration
- Fast build process

**Output:**
- `dist/SpanishConjugation.exe` - Single executable file
- `SpanishConjugation_Distribution/` - Ready-to-distribute folder

### Method 2: Advanced Build (build_advanced.py)

Best for: Production releases

```bash
python build_advanced.py
```

**Features:**
- Comprehensive dependency detection
- Version management and metadata
- Asset creation and bundling
- Build validation and testing
- Automatic distribution packaging
- Detailed build reporting

**Configuration:** Uses `build_config.json` for settings

**Output:**
- Versioned executable with metadata
- Distribution ZIP archive
- Comprehensive build report

### Method 3: Enhanced Spec File

Best for: Custom PyInstaller configurations

```bash
pyinstaller SpanishConjugation_Enhanced.spec
```

**Features:**
- Comprehensive hidden imports
- Custom PyInstaller hooks
- Resource bundling configuration
- Windows-specific optimizations
- Icon and version information

## ⚙️ Configuration

### Build Configuration (build_config.json)

```json
{
  "app": {
    "name": "SpanishConjugation",
    "display_name": "Spanish Conjugation Practice",
    "version": "2.0.0",
    "description": "Spanish Conjugation Practice with AI-powered feedback",
    "author": "Spanish Learning Tools",
    "copyright": "Copyright 2024",
    "homepage": "https://github.com/yourusername/conjugation_gui"
  },
  "build": {
    "one_file": true,
    "console": false,
    "debug": false,
    "upx": true,
    "optimize": 2,
    "clean": true
  },
  "resources": {
    "icon": "assets/icon.ico",
    "data_files": [
      {"source": "app_config.json", "destination": "."},
      {"source": ".env.example", "destination": "."}
    ],
    "exclude_modules": [
      "tkinter", "matplotlib", "numpy", "scipy",
      "pandas", "IPython", "jupyter", "tornado"
    ]
  },
  "distribution": {
    "create_installer": true,
    "installer_type": "nsis",
    "include_vcredist": true,
    "create_portable": true
  }
}
```

### Version Management

The build system supports automatic version management:

- **Git tags**: `v1.0.0` → Version `1.0.0`
- **Git commits**: Auto-generates `1.0.0-dev.123` format
- **Manual**: Set in `build_config.json`

Version information is embedded in:
- Executable metadata
- Installer properties
- Distribution filenames
- GitHub releases

### Asset Configuration

#### Icons
Place icon files in `assets/` directory:
- `assets/icon.ico` - Application icon (64x64, 32x32, 16x16)
- `assets/header.bmp` - Installer header (150x57)
- `assets/wizard.bmp` - Installer wizard (164x314)

If icons don't exist, the build system creates default ones using PIL.

#### Data Files
Automatically included:
- `app_config.json` - Application configuration
- `.env.example` - Environment file template
- `README.md` - Documentation (if exists)
- `LICENSE` - License file (if exists)

## 🔧 Advanced Build Options

### PyInstaller Hooks

Custom hooks in `pyinstaller_hooks/` directory:

- `hook-openai.py` - OpenAI package support
- `hook-PyQt5.py` - PyQt5 platform plugins
- `hook-requests.py` - SSL certificates
- `hook-dotenv.py` - Environment file handling

### Hidden Imports

Automatically included critical modules:
```python
hiddenimports = [
    'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
    'openai', 'requests', 'dotenv', 'PIL',
    'ssl', 'certifi', 'sqlite3', 'json'
]
```

### Runtime Hooks

`runtime_hooks.py` sets up the environment:
- Path configuration
- SSL certificate location
- Qt plugin paths
- Logging directories

### Build Optimizations

- **UPX Compression**: Reduces executable size by ~30%
- **Module Exclusion**: Removes unused modules
- **Import Optimization**: Only includes necessary submodules
- **Resource Bundling**: Efficient asset packaging

## 📦 Creating Installers

### NSIS Installer

Creates professional Windows installer with:

```bash
python build_installer.py
```

**Features:**
- API key configuration during installation
- Desktop and Start Menu shortcuts
- Proper uninstaller with registry entries
- Visual C++ Redistributable detection
- Windows version compatibility checks
- Professional installer UI with graphics

**Generated Files:**
- `SpanishConjugationSetup_v2.0.0.exe` - Complete installer
- Includes executable, support files, and configuration

### Installer Components

The installer includes:
- **Core Application** - Main executable (required)
- **Desktop Shortcut** - Desktop launcher (optional)
- **Start Menu Shortcuts** - Start Menu entries (default)
- **VC++ Redistributable** - Runtime dependencies (as needed)

### API Key Setup

The installer prompts for OpenAI API key during installation:
- Validates key format
- Creates secure `.env` file
- Sets appropriate file permissions
- Provides helpful error messages

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

#### Build Workflow (`.github/workflows/build-windows.yml`)

**Triggers:**
- Push to main/develop branches
- Git tags (releases)
- Manual workflow dispatch

**Jobs:**
1. **Compatibility Check** - System validation
2. **Build Executable** - Create Windows executable
3. **Build Installer** - Create NSIS installer
4. **Security Scan** - Windows Defender scan
5. **Create Release** - GitHub release creation

**Artifacts:**
- Windows executable
- Distribution ZIP
- NSIS installer
- Compatibility reports

#### Test Workflow (`.github/workflows/test.yml`)

**Jobs:**
1. **Lint and Format** - Code quality checks
2. **Unit Tests** - Cross-platform testing
3. **Integration Tests** - Application startup tests
4. **Build Validation** - Build system tests
5. **Security Audit** - Dependency vulnerability scan

### Automated Releases

When you push a git tag:

```bash
git tag v2.0.0
git push origin v2.0.0
```

The CI/CD pipeline automatically:
1. Builds executable and installer
2. Runs security scans
3. Creates GitHub release
4. Uploads distribution files
5. Generates release notes

## 🐛 Troubleshooting

### Common Build Issues

#### "PyInstaller not found"
```bash
pip install pyinstaller
# Ensure it's in PATH
pyinstaller --version
```

#### "Missing module" errors
Add to hidden imports in spec file:
```python
hiddenimports = ['missing_module_name']
```

#### "SSL certificate" errors
```bash
pip install --upgrade certifi
```

#### Large executable size
- Enable UPX compression
- Add more modules to exclude list
- Check for unnecessary imports

#### Executable won't start
1. Run compatibility check: `python compatibility_check.py`
2. Check Windows Defender exclusions
3. Install Visual C++ Redistributable
4. Run executable from command prompt to see errors

### Build Validation Issues

Run validation script to diagnose:
```bash
python validate_build.py
```

Common fixes:
- **Missing dependencies**: `pip install -r requirements.txt`
- **Invalid spec file**: Check syntax in PyInstaller spec
- **Missing resources**: Ensure all data files exist
- **Permission issues**: Run as administrator

### Installer Issues

#### NSIS not found
```bash
# Install NSIS
choco install nsis
# Or download from: https://nsis.sourceforge.io/
```

#### Installer crashes
- Check NSIS script syntax
- Verify all required files exist
- Test installer in VM

### Distribution Issues

#### Antivirus false positives
1. Add Windows Defender exclusions
2. Consider code signing certificate
3. Submit to antivirus vendors for whitelisting

#### Missing dependencies on target system
- Include Visual C++ Redistributable in installer
- Test on clean Windows installation
- Check system requirements

## 📤 Distribution

### Distribution Checklist

Before releasing:

- [ ] Run full compatibility check
- [ ] Test on clean Windows system
- [ ] Verify API key configuration works
- [ ] Test all application features
- [ ] Check installer creates proper shortcuts
- [ ] Verify uninstaller works correctly
- [ ] Test with Windows Defender active
- [ ] Document system requirements
- [ ] Create user installation guide

### File Structure

Distribution package contains:
```
SpanishConjugation_v2.0.0_Windows/
├── SpanishConjugation.exe      # Main executable
├── .env.example                # API key template
├── Launch.bat                  # Helper launch script
├── README.txt                  # Installation instructions
└── INSTALL.md                  # Detailed setup guide
```

### Code Signing (Recommended)

For production releases, consider code signing:

1. **Obtain Certificate**: Get from certificate authority
2. **Sign Executable**: Use `signtool.exe`
3. **Verify Signature**: Check certificate validity
4. **Update Installer**: Sign installer too

Benefits:
- Reduces antivirus false positives
- Shows publisher identity
- Enables SmartScreen bypass
- Builds user trust

### Distribution Channels

Consider these distribution methods:

- **GitHub Releases** - Direct download
- **Microsoft Store** - Official app store
- **Company Website** - Custom download page
- **Software Portals** - Third-party sites

## 📚 Additional Resources

### Documentation Files

- `BUILD.md` - This build guide
- `README.md` - Application overview
- `CONTRIBUTING.md` - Development guide
- `compatibility_report.txt` - System compatibility results
- `validation_report.txt` - Build validation results

### Build Scripts

- `build_exe.py` - Simple build script
- `build_advanced.py` - Advanced build with features
- `build_installer.py` - NSIS installer creation
- `validate_build.py` - Build validation
- `compatibility_check.py` - System compatibility
- `windows_config.py` - Windows-specific utilities

### Configuration Files

- `build_config.json` - Build configuration
- `SpanishConjugation_Enhanced.spec` - PyInstaller spec
- `installer.nsi` - NSIS installer script
- `.github/workflows/` - CI/CD workflows

### Support

For build issues:
1. Check this documentation
2. Run validation scripts
3. Review GitHub Actions logs
4. Check project issues on GitHub

---

## 🎉 Success!

If you've followed this guide, you should now have:

- ✅ A working Windows executable
- ✅ Professional NSIS installer
- ✅ Automated CI/CD pipeline
- ✅ Comprehensive testing and validation
- ✅ Distribution-ready packages

Your Spanish Conjugation Practice application is ready for professional deployment on Windows systems!

---

*Last updated: 2024-08-24*
*Version: 2.0.0*