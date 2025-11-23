# Spanish Conjugation Practice - Installation Guide 🚀

Complete installation guide for the Spanish Conjugation Practice desktop application across all supported platforms.

## 📋 System Requirements

### Minimum System Requirements

| Component | Windows | macOS | Linux |
|-----------|---------|--------|-------|
| **OS Version** | Windows 10 64-bit | macOS 10.14 (Mojave) | Ubuntu 20.04 LTS |
| **RAM** | 2 GB | 2 GB | 2 GB |
| **Storage** | 150 MB free space | 150 MB free space | 200 MB free space |
| **Display** | 1366x768 | 1366x768 | 1366x768 |
| **Internet** | Optional* | Optional* | Optional* |

### Recommended System Requirements

| Component | Windows | macOS | Linux |
|-----------|---------|--------|-------|
| **OS Version** | Windows 11 | macOS 12 (Monterey) | Ubuntu 22.04 LTS |
| **RAM** | 4 GB | 4 GB | 4 GB |
| **Storage** | 500 MB free space | 500 MB free space | 500 MB free space |
| **Display** | 1920x1080 | 1920x1080 | 1920x1080 |
| **Internet** | Broadband | Broadband | Broadband |

*Internet connection is only required for AI-powered features (OpenAI integration). The application works fully offline for basic conjugation practice.

## 🖥️ Windows Installation

### Option 1: Pre-built Executable (Recommended)

#### Download and Install

1. **Download the Windows Package**
   - Visit the [Releases page](https://github.com/yourusername/conjugation_gui/releases)
   - Download `SpanishConjugation-Windows.zip` (approximately 45-60 MB)
   - Save to your Downloads folder or preferred location

2. **Extract the Application**
   ```
   Right-click SpanishConjugation-Windows.zip
   → Select "Extract All..."
   → Choose destination (e.g., C:\Programs\SpanishConjugation\)
   → Click "Extract"
   ```

3. **Verify Installation**
   Your installation folder should contain:
   ```
   SpanishConjugation_Distribution/
   ├── SpanishConjugation.exe    # Main application (≈45 MB)
   ├── Run.bat                   # Launcher script
   ├── .env.example              # API configuration template
   ├── README.txt                # Quick start guide
   └── _internal/                # Application dependencies
   ```

4. **Create Desktop Shortcut (Optional)**
   ```
   Right-click SpanishConjugation.exe
   → Send to → Desktop (create shortcut)
   ```

#### First Launch

1. **Run the Application**
   - **Recommended**: Double-click `Run.bat` (handles API key setup)
   - **Alternative**: Double-click `SpanishConjugation.exe` directly

2. **Handle Windows Security Warning**
   If Windows shows "Windows protected your PC":
   ```
   Click "More info"
   → Click "Run anyway"
   ```

3. **Allow Firewall Access (if prompted)**
   ```
   Click "Allow access" when Windows Firewall prompts
   (Only needed for AI features that connect to OpenAI)
   ```

### Option 2: Installer Package (Coming Soon)

A Windows installer (.msi) will be available in future releases for automatic installation, Start Menu integration, and uninstall support.

### Troubleshooting Windows Installation

#### Issue: "VCRUNTIME140.dll was not found"
**Solution**: Install Microsoft Visual C++ Redistributable
```
1. Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Run the installer as administrator
3. Restart your computer
4. Try launching the application again
```

#### Issue: Windows Defender blocks the application
**Solution**: Add security exception
```
1. Open Windows Security
2. Go to Virus & threat protection
3. Click "Manage settings" under Virus & threat protection settings
4. Click "Add or remove exclusions"
5. Add folder exclusion for your installation directory
```

#### Issue: Application appears to start but no window shows
**Solution**: Check display scaling
```
1. Right-click SpanishConjugation.exe
2. Select Properties → Compatibility tab
3. Check "Override high DPI scaling behavior"
4. Set scaling performed by: Application
```

## 🍎 macOS Installation

### Option 1: DMG Package (Recommended)

#### Download and Install

1. **Download the macOS Package**
   - Visit the [Releases page](https://github.com/yourusername/conjugation_gui/releases)
   - Download `SpanishConjugation-macOS.dmg` (approximately 50-70 MB)

2. **Mount and Install**
   ```
   Double-click SpanishConjugation-macOS.dmg
   → Drag SpanishConjugation.app to Applications folder
   → Eject the disk image
   ```

3. **First Launch**
   ```
   Open Applications folder
   → Double-click SpanishConjugation.app
   ```

#### Handle macOS Security (Gatekeeper)

1. **If you see "cannot be opened because it is from an unidentified developer"**:
   ```
   Right-click SpanishConjugation.app
   → Select "Open"
   → Click "Open" in the confirmation dialog
   ```

2. **Alternative method**:
   ```
   System Preferences → Security & Privacy
   → Click "Open Anyway" next to the blocked app message
   ```

3. **For persistent issues, use Terminal**:
   ```bash
   xattr -cr /Applications/SpanishConjugation.app
   ```

### Option 2: Homebrew Installation (Coming Soon)

Future releases will support Homebrew installation:
```bash
brew install --cask spanish-conjugation-practice
```

### Troubleshooting macOS Installation

#### Issue: "SpanishConjugation.app is damaged and can't be opened"
**Solution**: Remove quarantine attribute
```bash
# Open Terminal and run:
sudo xattr -r -d com.apple.quarantine /Applications/SpanishConjugation.app
```

#### Issue: Application crashes on startup
**Solution**: Check Console for error messages
```
1. Open Console.app (in Utilities)
2. Filter for "SpanishConjugation"
3. Launch the app and check for error messages
4. Common fix: Ensure macOS is 10.14 or later
```

#### Issue: High memory usage
**Solution**: macOS Rosetta (for Intel Macs running Apple Silicon)
```
Right-click SpanishConjugation.app
→ Get Info
→ Check "Open using Rosetta" (if available)
```

## 🐧 Linux Installation

### Ubuntu/Debian Installation

#### Option 1: AppImage (Recommended)

1. **Download AppImage**
   ```bash
   wget https://github.com/yourusername/conjugation_gui/releases/download/v1.0.0/SpanishConjugation-x86_64.AppImage
   ```

2. **Make Executable and Run**
   ```bash
   chmod +x SpanishConjugation-x86_64.AppImage
   ./SpanishConjugation-x86_64.AppImage
   ```

3. **Optional: Install AppImageLauncher for system integration**
   ```bash
   sudo add-apt-repository ppa:appimagelauncher-team/stable
   sudo apt update
   sudo apt install appimagelauncher
   ```

#### Option 2: Debian Package

1. **Download .deb Package**
   ```bash
   wget https://github.com/yourusername/conjugation_gui/releases/download/v1.0.0/spanish-conjugation-practice_1.0.0_amd64.deb
   ```

2. **Install with apt**
   ```bash
   sudo apt install ./spanish-conjugation-practice_1.0.0_amd64.deb
   ```

3. **Launch from Applications Menu**
   ```
   Applications → Education → Spanish Conjugation Practice
   ```

#### Option 3: Compiled Binary

1. **Download and Extract**
   ```bash
   wget https://github.com/yourusername/conjugation_gui/releases/download/v1.0.0/SpanishConjugation-Linux.tar.gz
   tar -xzf SpanishConjugation-Linux.tar.gz
   cd SpanishConjugation_Distribution
   ```

2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install libxcb-xinerama0 libxcb-cursor0 libegl1-mesa
   ```

3. **Run Application**
   ```bash
   ./SpanishConjugation
   ```

### CentOS/RHEL/Fedora Installation

#### Install Dependencies
```bash
# CentOS/RHEL 8+
sudo dnf install qt5-qtbase qt5-qtwebengine

# Fedora
sudo dnf install qt5-qtbase qt5-qtwebengine

# Older CentOS/RHEL
sudo yum install qt5-qtbase qt5-qtwebengine
```

#### Download and Run
```bash
wget https://github.com/yourusername/conjugation_gui/releases/download/v1.0.0/SpanishConjugation-Linux.tar.gz
tar -xzf SpanishConjugation-Linux.tar.gz
cd SpanishConjugation_Distribution
chmod +x SpanishConjugation
./SpanishConjugation
```

### Arch Linux Installation

#### Option 1: AUR Package (Coming Soon)
```bash
yay -S spanish-conjugation-practice
# or
paru -S spanish-conjugation-practice
```

#### Option 2: Manual Installation
```bash
# Install dependencies
sudo pacman -S qt5-base qt5-webengine

# Download and run
wget https://github.com/yourusername/conjugation_gui/releases/download/v1.0.0/SpanishConjugation-Linux.tar.gz
tar -xzf SpanishConjugation-Linux.tar.gz
cd SpanishConjugation_Distribution
chmod +x SpanishConjugation
./SpanishConjugation
```

### Troubleshooting Linux Installation

#### Issue: "libQt5Core.so.5: cannot open shared object file"
**Solution**: Install Qt5 dependencies
```bash
# Ubuntu/Debian
sudo apt install qt5-default libqt5widgets5

# CentOS/RHEL/Fedora
sudo dnf install qt5-qtbase qt5-qtbase-gui

# Arch
sudo pacman -S qt5-base
```

#### Issue: "Permission denied" when running binary
**Solution**: Make executable
```bash
chmod +x SpanishConjugation
```

#### Issue: Application doesn't appear in system menu
**Solution**: Create desktop entry manually
```bash
cat > ~/.local/share/applications/spanish-conjugation.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Spanish Conjugation Practice
Comment=Learn Spanish verb conjugations
Exec=/path/to/SpanishConjugation_Distribution/SpanishConjugation
Icon=/path/to/SpanishConjugation_Distribution/icon.png
Terminal=false
Categories=Education;Language;
EOF
```

## 🔑 API Key Configuration

### Getting OpenAI API Key

1. **Create OpenAI Account**
   - Visit [OpenAI Platform](https://platform.openai.com)
   - Sign up for an account
   - Verify your email address

2. **Add Payment Method** (Required for API access)
   - Go to [Billing](https://platform.openai.com/account/billing)
   - Add a payment method
   - Set usage limits for cost control

3. **Generate API Key**
   - Navigate to [API Keys](https://platform.openai.com/api-keys)
   - Click "Create new secret key"
   - Name your key (e.g., "Spanish Conjugation App")
   - **Important**: Copy the key immediately - you won't be able to see it again!

### Configuring API Key in the Application

#### Method 1: Using .env File (Recommended)

1. **Locate Configuration File**
   - **Windows**: In your installation directory
   - **macOS**: Right-click app → Show Package Contents → Contents → Resources
   - **Linux**: In your installation directory

2. **Copy and Rename Template**
   ```bash
   # Copy .env.example to .env
   cp .env.example .env
   ```

3. **Edit Configuration**
   Open `.env` in any text editor and replace:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   With:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

4. **Optional: Additional Configuration**
   ```
   OPENAI_MODEL=gpt-4o
   OPENAI_MAX_TOKENS=600
   OPENAI_TEMPERATURE=0.5
   ```

#### Method 2: Using Application Settings

1. **Launch Application**
2. **Open Settings** (⚙️ button or File → Settings)
3. **Go to API Configuration tab**
4. **Enter your API key** in the designated field
5. **Click "Test Connection"** to verify
6. **Save settings**

### API Key Security Best Practices

#### ✅ Do This:
- Store API key in `.env` file only
- Keep `.env` file in your installation directory
- Use different API keys for different applications
- Set spending limits in your OpenAI account
- Regularly rotate API keys

#### ❌ Don't Do This:
- Share your API key with anyone
- Commit `.env` file to version control
- Use API keys on shared computers without removing them afterward
- Store API keys in screenshots or plain text files
- Use the same API key across multiple applications

#### Monitor Usage
- Check your usage at [OpenAI Usage](https://platform.openai.com/account/usage)
- Set up billing alerts for cost control
- Review API logs regularly

### Working Without API Keys (Offline Mode)

The application is fully functional without API keys! You'll have access to:

✅ **Available Features**:
- Complete Spanish verb database (100+ verbs)
- All conjugation tenses and persons
- Progress tracking and statistics
- Spaced repetition learning
- Speed practice mode
- Custom exercise creation
- Export/import functionality

❌ **Unavailable Features**:
- AI-generated explanations and hints
- Dynamic story mode
- Contextual exercise generation
- Advanced task scenarios

## 🚦 Verification and First Launch

### Testing Installation

1. **Launch Application**
   - Use the appropriate method for your platform
   - Wait for the application window to appear (may take 10-15 seconds on first launch)

2. **Check Core Functions**
   ```
   ✓ Application window opens
   ✓ "New Exercise" button generates a practice question
   ✓ Can type answers in the input field
   ✓ "Submit" provides feedback
   ✓ Progress statistics are visible
   ```

3. **Test API Connection (if configured)**
   ```
   Settings → API Configuration → Test Connection
   ✓ Should show "Connection successful" message
   ```

### Performance Verification

1. **Startup Time**: Should launch within 15 seconds
2. **Memory Usage**: Should use less than 100 MB RAM
3. **Responsiveness**: UI should respond immediately to clicks
4. **Exercise Generation**: Should create new exercises within 2 seconds

### Setting Up for First Use

1. **Choose Learning Level**
   - Beginner: Present tense only, common verbs
   - Intermediate: Present, preterite, imperfect tenses
   - Advanced: All tenses and irregular verbs

2. **Select Practice Preferences**
   - Tenses to practice
   - Persons to include (yo, tú, él, etc.)
   - Show hints when stuck
   - Enable progress tracking

3. **Start Your First Session**
   - Click "New Exercise"
   - Complete 5-10 exercises to establish baseline
   - Review your progress in the Statistics panel

## 🔄 Updates and Maintenance

### Automatic Updates (Future Feature)

Future versions will include automatic update checking and installation.

### Manual Updates

1. **Check for Updates**
   - Visit the [Releases page](https://github.com/yourusername/conjugation_gui/releases)
   - Compare your version (Help → About) with the latest release

2. **Download New Version**
   - Download the latest package for your platform
   - Your progress data and settings will be preserved

3. **Install Update**
   - Follow the same installation process
   - Your existing `.env` file will be automatically detected

### Backup Your Progress

Before major updates, backup your data:

```bash
# Your progress is stored in these files:
# Windows: %USERPROFILE%\AppData\Local\SpanishConjugation\
# macOS: ~/Library/Application Support/SpanishConjugation/
# Linux: ~/.local/share/SpanishConjugation/

# Files to backup:
- progress.db       # Your learning progress
- .env             # API configuration
- user_settings.json # Application preferences
```

## 🆘 Getting Help

### Common Installation Issues

| Problem | Solution | Platform |
|---------|----------|----------|
| Won't start | Install Visual C++ Redistributable | Windows |
| Security warning | Add security exception | Windows |
| "Unidentified developer" | Right-click → Open | macOS |
| "App is damaged" | Remove quarantine with xattr | macOS |
| Missing libraries | Install Qt5 packages | Linux |
| Permission denied | chmod +x on executable | Linux |

### Support Resources

- 📖 **Documentation**: [USER_GUIDE.md](USER_GUIDE.md)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/conjugation_gui/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/yourusername/conjugation_gui/discussions)
- 📧 **Email Support**: your.email@example.com

### Reporting Installation Issues

When reporting problems, please include:

1. **System Information**
   - Operating system and version
   - Available RAM and storage
   - Python version (if running from source)

2. **Installation Details**
   - Download source and file name
   - Installation method used
   - Error messages (exact text)

3. **Steps to Reproduce**
   - What you did before the error
   - When the error occurs
   - Any workarounds you tried

---

## ✅ Installation Checklist

Before you start learning:

- [ ] Downloaded correct version for your platform
- [ ] Successfully extracted/installed application  
- [ ] Application launches without errors
- [ ] Created `.env` file with API key (optional)
- [ ] Tested API connection (if using AI features)
- [ ] Completed first-time setup wizard
- [ ] Generated and completed first exercise
- [ ] Verified progress tracking is working
- [ ] Created desktop shortcut (optional)
- [ ] Bookmarked this guide for reference

**¡Felicidades!** You're ready to start mastering Spanish verb conjugations! 🎉

---

**Need additional help?** Check the [User Guide](USER_GUIDE.md) for detailed usage instructions or the [Troubleshooting section](USER_GUIDE.md#troubleshooting) for common issues.