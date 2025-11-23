# Spanish Conjugation Practice App - User Guide 📚

Welcome to the Spanish Conjugation Practice App! This comprehensive desktop application helps you master Spanish verb conjugations through interactive exercises, AI-powered learning, and adaptive practice modes.

## 🚀 Quick Start

### System Requirements

#### Minimum Requirements
- **Operating System**: 
  - Windows 10 (64-bit) or later
  - macOS 10.14 (Mojave) or later
  - Ubuntu 20.04 LTS or equivalent Linux distribution
- **Memory (RAM)**: 2 GB available RAM
- **Storage**: 150 MB free disk space
- **Display**: 1366x768 resolution
- **Internet**: Optional (required only for AI features)

#### Recommended Requirements
- **Memory (RAM)**: 4 GB or more
- **Storage**: 500 MB free disk space
- **Display**: 1920x1080 resolution or higher
- **Internet**: Stable broadband connection for AI features

## 📥 Installation

### Option 1: Pre-built Executable (Recommended)

#### For Windows Users

1. **Download the Application**
   - Download `SpanishConjugation-Windows.zip` from the releases section
   - File size: approximately 45-60 MB

2. **Extract Files**
   - Right-click the ZIP file and select "Extract All..."
   - Choose a destination folder (e.g., `C:\Program Files\SpanishConjugation\`)
   - Click "Extract"

3. **Verify Contents**
   Your extracted folder should contain:
   ```
   SpanishConjugation_Distribution/
   ├── SpanishConjugation.exe    # Main application
   ├── Run.bat                   # Launch script
   ├── .env.example              # API configuration template
   └── README.txt                # Quick start guide
   ```

#### For macOS Users

1. **Download the Application**
   - Download `SpanishConjugation-macOS.dmg`
   - Double-click to mount the disk image

2. **Install Application**
   - Drag `SpanishConjugation.app` to your Applications folder
   - If macOS shows a security warning:
     - Go to System Preferences > Security & Privacy
     - Click "Open Anyway" for SpanishConjugation
   
3. **Alternative: Command Line**
   ```bash
   # Remove quarantine attribute if needed
   xattr -cr /Applications/SpanishConjugation.app
   ```

#### For Linux Users

1. **Download the Application**
   - Download `SpanishConjugation-Linux.tar.gz`
   - Extract using: `tar -xzf SpanishConjugation-Linux.tar.gz`

2. **Make Executable**
   ```bash
   cd SpanishConjugation_Distribution/
   chmod +x SpanishConjugation
   ```

3. **Install Dependencies** (if needed)
   ```bash
   # Ubuntu/Debian
   sudo apt install libxcb-xinerama0 libxcb-cursor0
   
   # CentOS/RHEL/Fedora
   sudo yum install libxcb
   ```

### Option 2: Run from Source (Developers)

See the [Developer Documentation](DEVELOPER_GUIDE.md) for detailed instructions.

## 🔑 API Key Configuration

The application supports both offline and online modes. For enhanced AI-powered features, you'll need an OpenAI API key.

### Getting Your OpenAI API Key

#### Step 1: Create OpenAI Account
1. Visit [OpenAI Platform](https://platform.openai.com)
2. Click "Sign Up" or "Log In" if you already have an account
3. Complete the registration process

#### Step 2: Generate API Key
1. Navigate to the [API Keys section](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Give your key a descriptive name (e.g., "Spanish Conjugation App")
4. Click "Create secret key"
5. **Important**: Copy the key immediately - you won't be able to see it again!

#### Step 3: Configure the Application
1. In your application folder, find `.env.example`
2. Copy this file and rename it to `.env`
3. Open `.env` in a text editor (Notepad, TextEdit, etc.)
4. Replace `your_openai_api_key_here` with your actual API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```
5. Save the file

### Alternative: Claude AI Support (Coming Soon)
Future versions will support Claude AI. Configuration will be similar:
```
CLAUDE_API_KEY=your_claude_api_key_here
```

### Using Without API Keys (Offline Mode)
The application works perfectly without any API keys! You'll have access to:
- ✅ 100+ built-in Spanish verbs
- ✅ All conjugation tenses
- ✅ Progress tracking
- ✅ Speed practice mode
- ✅ Custom exercises
- ❌ AI-generated hints and explanations
- ❌ Dynamic story mode
- ❌ Advanced task scenarios

## 🎯 First Run Setup

### Screenshot Mockups

#### Launch Screen
```
┌─────────────────────────────────────────────────────────┐
│ Spanish Conjugation Practice                    [_][□][×]│
├─────────────────────────────────────────────────────────┤
│                                                         │
│        🇪🇸 ¡Bienvenidos! Welcome! 🇪🇸                │
│                                                         │
│     Master Spanish verb conjugations with              │
│     interactive exercises and AI-powered learning      │
│                                                         │
│  [🔧 First Time Setup]  [🚀 Start Practicing]         │
│                                                         │
│  Status: ● Offline Mode (No API key configured)        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Setup Wizard - Step 1
```
┌─────────────────────────────────────────────────────────┐
│ Setup Wizard - API Configuration           [_][□][×]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1 of 3: Choose Your Learning Mode                │
│                                                         │
│  ○ Offline Mode (No API key required)                  │
│    • Works with built-in verb database                 │
│    • All basic features available                      │
│    • No internet connection needed                     │
│                                                         │
│  ○ Enhanced Mode (OpenAI API required)                 │
│    • AI-powered hints and explanations                 │
│    • Dynamic story generation                          │
│    • Advanced conversation practice                    │
│                                                         │
│  ○ Skip Setup (Configure later)                        │
│                                                         │
│                    [Back]  [Continue]                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Setup Wizard - Step 2 (Enhanced Mode)
```
┌─────────────────────────────────────────────────────────┐
│ Setup Wizard - API Key Entry               [_][□][×]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 2 of 3: Enter Your OpenAI API Key                │
│                                                         │
│  API Key: [sk-your-key-here________________] [👁]      │
│                                                         │
│  💡 Don't have an API key?                             │
│  1. Visit https://platform.openai.com/api-keys         │
│  2. Create new secret key                              │
│  3. Copy and paste above                               │
│                                                         │
│  🔐 Your API key is stored locally and encrypted       │
│                                                         │
│  [🧪 Test Connection]                                  │
│                                                         │
│  Status: ● Ready to test                               │
│                                                         │
│                    [Back]  [Continue]                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Setup Wizard - Step 3
```
┌─────────────────────────────────────────────────────────┐
│ Setup Wizard - Learning Preferences        [_][□][×]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 3 of 3: Customize Your Experience                │
│                                                         │
│  Difficulty Level:                                      │
│  ○ Beginner    ○ Intermediate    ● Advanced            │
│                                                         │
│  Focus Areas: (Select all that apply)                  │
│  ☑ Present Tense      ☑ Preterite        ☐ Imperfect  │
│  ☑ Future Tense       ☐ Conditional      ☐ Subjunctive │
│                                                         │
│  Practice Preferences:                                  │
│  ☑ Show hints when stuck                               │
│  ☑ Track progress statistics                           │
│  ☐ Enable speed challenges                             │
│                                                         │
│  Language Interface:                                    │
│  ● English    ○ Spanish    ○ Bilingual                 │
│                                                         │
│                    [Back]  [Finish Setup]              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### First-Time Setup Instructions

1. **Launch the Application**
   - **Windows**: Double-click `Run.bat` or `SpanishConjugation.exe`
   - **macOS**: Open `SpanishConjugation.app` from Applications
   - **Linux**: Run `./SpanishConjugation` in terminal

2. **Choose Learning Mode**
   - Select **Offline Mode** for immediate use without API keys
   - Select **Enhanced Mode** if you have an OpenAI API key
   - You can always change this later in Settings

3. **Configure API (Enhanced Mode Only)**
   - Enter your OpenAI API key
   - Click "Test Connection" to verify it works
   - The key will be encrypted and stored locally

4. **Set Learning Preferences**
   - Choose your current Spanish level
   - Select which tenses you want to practice
   - Configure practice options
   - Set interface language

5. **Start Learning!**
   - Click "Finish Setup" to save your preferences
   - You'll be taken to the main practice interface
   - Click "New Exercise" to begin your first lesson

## 🎮 Using the Application

### Main Interface Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ Spanish Conjugation Practice                        [_][□][×]    │
├─────────────────────────────────────────────────────────────────┤
│ File  Practice  Tools  Help                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─── Exercise Panel ──────────────────────────────────────────┐ │
│ │                                                             │ │
│ │  Conjugate "hablar" (to speak) in Present Tense            │ │
│ │                                                             │ │
│ │  Yo _________ español todos los días.                       │ │
│ │  (I speak Spanish every day.)                               │ │
│ │                                                             │ │
│ │  Your Answer: [hablo___________] [Submit] [💡 Hint]        │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─── Practice Controls ────────────────────┐ ┌─── Stats ─────┐ │
│ │ [📝 New Exercise]  [⚡ Speed Mode]       │ │ Correct: 85%  │ │
│ │ [🎯 Task Practice] [📖 Story Mode]      │ │ Streak: 12    │ │
│ │ [⚙️ Settings]      [📊 Progress]         │ │ Level: Int.   │ │
│ └──────────────────────────────────────────┘ └───────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Practice Modes

#### 1. Standard Practice Mode 📝
- **Purpose**: Systematic learning of verb conjugations
- **How to Use**:
  1. Click "New Exercise"
  2. Select tenses and persons to practice
  3. Choose difficulty level (Beginner/Intermediate/Advanced)
  4. Type your answers and click "Submit"
  5. Review explanations and continue

#### 2. Speed Practice Mode ⚡
- **Purpose**: Build fluency and automatic recall
- **How to Use**:
  1. Click "Speed Mode"
  2. Set timer (1-10 seconds per question)
  3. Answer as quickly as possible
  4. Track your speed improvement over time

#### 3. Task-Based Practice 🎯
- **Purpose**: Real-world communication scenarios
- **How to Use**:
  1. Click "Task Practice"
  2. Choose a scenario (restaurant, travel, work, etc.)
  3. Complete conjugation challenges in context
  4. Apply verbs in meaningful situations

#### 4. Story Mode 📖 (Enhanced Mode Only)
- **Purpose**: Connected narrative practice
- **How to Use**:
  1. Click "Story Mode"
  2. AI generates a cohesive story
  3. Fill in conjugated verbs to continue the narrative
  4. Experience verbs in natural context

### Getting Help and Hints

#### Built-in Help System
- **Conjugation Rules**: Click any verb to see conjugation patterns
- **Grammar Tips**: Hover over exercises for quick explanations
- **Progress Guidance**: Get suggestions for areas needing improvement

#### AI-Powered Hints (Enhanced Mode)
- **Smart Hints**: Context-aware explanations
- **Grammar Explanations**: Detailed rule breakdowns
- **Common Mistakes**: Learn from typical errors

## 🛡️ Security & Privacy

### API Key Security Best Practices

#### Protection Measures
1. **Local Storage Only**: Your API keys never leave your computer
2. **Encryption**: Keys are encrypted before storage
3. **No Sharing**: Never share your .env file or API keys
4. **Regular Rotation**: Change API keys periodically

#### What NOT to Do
- ❌ Never commit .env files to version control
- ❌ Don't share API keys in screenshots or messages
- ❌ Avoid using API keys on shared computers
- ❌ Don't store keys in unsecured text files

#### Recommended Practices
- ✅ Use different API keys for different applications
- ✅ Monitor your API usage on OpenAI dashboard
- ✅ Set usage limits on your API account
- ✅ Revoke unused API keys immediately

### Data Privacy

#### What We Store Locally
- ✅ Your practice progress and statistics
- ✅ Application settings and preferences
- ✅ Encrypted API keys (if provided)
- ✅ Learning analytics for improvement

#### What We Don't Store
- ❌ Personal information beyond what you provide
- ❌ Practice responses on external servers
- ❌ API keys in plain text
- ❌ Usage data sent to third parties

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Application Won't Start

**Issue**: Double-clicking the executable does nothing
- **Solution 1**: Check if Windows Defender is blocking it
  1. Go to Windows Security > Virus & threat protection
  2. Click "Manage settings" under Virus & threat protection settings
  3. Add an exclusion for the application folder
- **Solution 2**: Run as administrator
  1. Right-click `SpanishConjugation.exe`
  2. Select "Run as administrator"
- **Solution 3**: Check system requirements
  1. Ensure Windows 10 64-bit or later
  2. Verify 2GB+ RAM available

**Issue**: macOS shows "Cannot verify developer"
- **Solution**: 
  ```bash
  # In Terminal:
  xattr -cr /path/to/SpanishConjugation.app
  ```
  Or go to System Preferences > Security & Privacy > General > "Open Anyway"

#### API Connection Issues

**Issue**: "Invalid API key" error
- **Check**: Verify API key is correct in .env file
- **Check**: Ensure no extra spaces or characters
- **Check**: Confirm API key hasn't been revoked
- **Solution**: Regenerate API key on OpenAI platform

**Issue**: "Network connection failed"
- **Check**: Internet connection is working
- **Check**: Firewall isn't blocking the application
- **Solution**: Try switching to offline mode temporarily

**Issue**: "Rate limit exceeded" 
- **Cause**: Too many API requests in short time
- **Solution**: Wait 60 seconds and try again
- **Prevention**: Use offline mode for intensive practice

#### Performance Issues

**Issue**: Application runs slowly
- **Check**: Available RAM (need 2GB minimum)
- **Check**: Close other memory-intensive applications
- **Solution**: Lower exercise difficulty or batch size

**Issue**: High CPU usage
- **Cause**: AI processing in enhanced mode
- **Solution**: Switch to offline mode for better performance

#### Database and Progress Issues

**Issue**: Progress not saving
- **Check**: Write permissions in application folder
- **Solution**: Move application to Documents folder
- **Solution**: Run as administrator (Windows)

**Issue**: "Database corrupted" error
- **Solution**: Delete `progress.db` file (will reset progress)
- **Prevention**: Don't force-close the application

**Issue**: Statistics show incorrect data
- **Solution**: Go to Settings > Data > "Reset Statistics"
- **Note**: This will clear all progress data

### Advanced Troubleshooting

#### Log File Analysis
The application creates log files for debugging:
- **Location**: Same folder as executable
- **Files**: `session_log.txt`, `error_log.txt`
- **Usage**: Include these files when reporting issues

#### Command Line Diagnostics (Windows)
```cmd
# Run from Command Prompt to see error messages
cd "C:\path\to\SpanishConjugation_Distribution"
SpanishConjugation.exe --debug
```

#### Environment Variables Check
```bash
# Verify environment setup
echo $OPENAI_API_KEY  # Should show your key
echo $PATH           # Should include application directory
```

### Getting Additional Help

#### Documentation Resources
- **User Guide**: This document
- **Developer Guide**: For technical users
- **API Documentation**: OpenAI platform docs
- **Video Tutorials**: Available on project website

#### Community Support
- **GitHub Issues**: Report bugs and request features
- **Discussion Forums**: Community Q&A
- **Email Support**: For urgent issues

#### Reporting Bugs
When reporting issues, please include:
1. **Operating System**: Windows/macOS/Linux version
2. **Application Version**: Found in Help > About
3. **Error Message**: Exact text if available
4. **Steps to Reproduce**: What you did before the error
5. **Log Files**: session_log.txt if applicable

## 🚀 Advanced Features

### Custom Practice Creation
- **Verb Lists**: Create focused practice sets
- **Tense Combinations**: Practice specific combinations
- **Difficulty Scaling**: Progressive challenge levels
- **Export/Import**: Share practice sets with others

### Progress Analytics
- **Performance Tracking**: Detailed statistics
- **Learning Curves**: Visual progress representation
- **Weakness Identification**: Areas needing improvement
- **Achievement System**: Unlock practice milestones

### Integration Features
- **Export Data**: Save progress to CSV/JSON
- **Backup/Restore**: Protect your learning data
- **Settings Sync**: Share preferences across devices
- **Study Reminders**: Never miss practice sessions

---

## 📞 Need Help?

### Quick Support Checklist
- [ ] Checked this troubleshooting guide
- [ ] Verified system requirements
- [ ] Tested with offline mode
- [ ] Reviewed log files
- [ ] Tried restarting the application

### Contact Options
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/conjugation_gui/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/yourusername/conjugation_gui/discussions)
- 📧 **Direct Support**: your.email@example.com

---

**¡Buena suerte con tu aprendizaje del español!** 
*Good luck with your Spanish learning!*