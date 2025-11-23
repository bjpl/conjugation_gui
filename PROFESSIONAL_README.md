# Spanish Conjugation Trainer - Professional Edition

A sophisticated desktop application for mastering Spanish verb conjugations with AI-powered learning, professional UI design, and advanced features.

## 🆕 Professional Features

### 🎨 Professional Desktop Experience
- **First-Run Setup Wizard**: Guided configuration for new users
- **Professional Settings Dialog**: Comprehensive configuration management
- **System Tray Integration**: Minimize to tray with context menu and notifications
- **About Dialog**: Version info, credits, and license information
- **Enhanced Error Handling**: User-friendly error messages with solutions
- **Professional Styling**: Modern light/dark themes with professional design

### 🚀 Enhanced Features
- **Setup Wizard**: First-time user configuration flow
- **API Key Management**: Secure OpenAI API key configuration
- **Offline Mode**: Full functionality without internet connection
- **Professional Icons**: Custom-designed application icons and branding
- **Configuration Management**: Persistent settings and preferences
- **System Notifications**: Progress updates and achievements

## 📁 Project Structure

```
conjugation_gui/
├── main_professional.py           # Enhanced main application
├── src/                           # Professional components
│   ├── dialogs/                   # Professional dialogs
│   │   ├── setup_wizard.py        # First-run setup wizard
│   │   ├── settings_dialog.py     # Settings/preferences dialog
│   │   ├── about_dialog.py        # About dialog with version info
│   │   └── error_dialog.py        # Enhanced error handling
│   ├── gui/                       # GUI components
│   │   ├── system_tray.py         # System tray integration
│   │   └── professional_styling.py # Modern styling and themes
│   ├── utils/                     # Utility components
│   │   └── first_run_manager.py   # First-run detection and config
│   └── resources/                 # Application assets
│       ├── icon_generator.py      # Icon generation script
│       ├── app_icon.ico           # Windows application icon
│       ├── icon_*.png             # Various icon sizes
│       └── splash.png             # Splash screen image
└── [original files...]            # Original application files
```

## 🎯 Getting Started

### Running the Professional Version

```bash
# Run the enhanced professional version
python main_professional.py

# Or run the original version
python main.py
```

### First Run Experience

1. **Setup Wizard**: On first run, you'll see a professional setup wizard
2. **API Configuration**: Configure your OpenAI API key (optional)
3. **Learning Preferences**: Set your difficulty level and focus areas
4. **Theme Selection**: Choose between light and dark themes

### Key Professional Features

#### 🔧 Settings Dialog
Access via `Settings` menu or `Ctrl+,`:
- **API & AI Tab**: Configure OpenAI integration
- **Learning Tab**: Customize difficulty and practice preferences
- **Appearance Tab**: Theme and display options
- **Advanced Tab**: Data management and backup options

#### 🖥️ System Tray Integration
- **Minimize to Tray**: Continue running in background
- **Quick Actions**: Access features from tray menu
- **Notifications**: Get progress updates and achievements
- **Context Menu**: Full feature access without opening main window

#### 🎨 Professional Styling
- **Modern Themes**: Professional light and dark modes
- **Consistent Design**: Unified styling across all components
- **Professional Colors**: Carefully chosen color palette
- **Responsive Layout**: Adapts to different screen sizes

#### 🚨 Enhanced Error Handling
- **User-Friendly Messages**: Clear explanations of what went wrong
- **Solution Suggestions**: Actionable steps to resolve issues
- **API Error Analysis**: Specific guidance for API-related problems
- **Technical Details**: Collapsible technical information

## 🔑 API Key Configuration

### Through Setup Wizard
1. Run the application for the first time
2. Follow the setup wizard prompts
3. Enter your OpenAI API key when prompted
4. Test the connection

### Through Settings Dialog
1. Open `Settings` → `API & AI` tab
2. Enter your API key in the secure field
3. Click "Test Connection" to verify
4. Choose your preferred AI model

### Using Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_api_key_here
```

## 🎓 Usage Guide

### Practice Modes
- **Grammar Drills**: Traditional conjugation exercises
- **Speed Mode**: Timed practice for conversational fluency
- **Task Mode**: Real-world scenario-based practice
- **Story Mode**: Connected narrative exercises

### Learning Features
- **AI Explanations**: Intelligent feedback on mistakes
- **Progress Tracking**: Detailed statistics and analytics
- **Adaptive Learning**: Focuses on your weak areas
- **Custom Practice**: Create your own exercise sets

### Professional Tools
- **Export Progress**: Backup your learning data
- **Statistics View**: Detailed performance analytics
- **Verb Reference**: Quick conjugation lookup
- **Achievement System**: Track milestones and progress

## 🔧 Configuration

The application uses multiple configuration files:
- `app_config.json`: Project-level configuration
- `~/.spanish_conjugation_trainer/user_config.json`: User preferences
- `.env`: Environment variables (API keys)

### Key Settings
```json
{
  "api_model": "gpt-4o",
  "dark_mode": false,
  "offline_mode": false,
  "minimize_to_tray": true,
  "exercise_count": 5,
  "answer_strictness": "normal"
}
```

## 🎨 Themes and Styling

### Light Theme
- Professional blue primary color (#3498db)
- Clean white backgrounds
- Subtle shadows and borders
- High contrast for accessibility

### Dark Theme  
- Same blue accents on dark backgrounds
- Comfortable eye-friendly colors
- Consistent styling with light theme
- Professional appearance

## 📊 System Requirements

- **OS**: Windows 10+, macOS 10.14+, Linux
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB for application, additional for progress data
- **Internet**: Required for AI features (offline mode available)

## 🚀 Advanced Features

### System Tray Operations
- Double-click to show/hide main window
- Right-click for context menu access
- Notifications for session completion
- Background operation support

### Error Recovery
- Automatic offline mode switching on API errors
- Configuration backup and restore
- Graceful degradation when features unavailable
- User-guided troubleshooting

### Data Management
- Automatic configuration backups
- Progress data export/import
- Settings synchronization
- Privacy-focused data handling

## 🔒 Privacy and Security

- **API Keys**: Stored securely, never logged
- **Practice Data**: Kept locally by default
- **AI Interactions**: Only conjugation-related content sent to OpenAI
- **No Tracking**: No analytics or user tracking
- **Offline Mode**: Complete functionality without external connections

## 🆘 Troubleshooting

### API Issues
1. Check API key format (starts with "sk-")
2. Verify OpenAI account status and billing
3. Test connection in Settings
4. Use offline mode as fallback

### Performance Issues
1. Close unused applications
2. Check available RAM
3. Use offline mode for better performance
4. Reduce exercise count if needed

### UI Issues
1. Try switching themes (light/dark)
2. Check display scaling settings
3. Restart application
4. Reset window geometry in settings

## 📞 Support

For issues or questions:
1. Check the built-in Help menu
2. Review error messages and suggestions
3. Check GitHub issues page
4. Use offline mode if API issues persist

---

**Professional Edition Features**: Setup wizard, system tray integration, enhanced error handling, professional styling, configuration management, and comprehensive user experience improvements.