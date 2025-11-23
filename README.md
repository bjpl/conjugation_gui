# Spanish Conjugation Practice App

A comprehensive desktop application for mastering Spanish verb conjugations with AI-powered learning and offline capabilities.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15.7-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## Quick Start

### Option 1: Download Pre-built Executable (Windows)

1. Go to the [Releases](https://github.com/yourusername/conjugation_gui/releases) page
2. Download `SpanishConjugation-Windows.zip`
3. Extract the ZIP file
4. Run `SpanishConjugation.exe`
5. Enter your OpenAI API key when prompted (optional for online features)

### Option 2: Run from Source

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key (optional, only for online mode)

#### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/conjugation_gui.git
cd conjugation_gui
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up API key** (optional, for AI features)
```bash
# Create .env file from template
cp .env.example .env

# Edit .env and add your OpenAI API key
# On Windows: notepad .env
# On Mac/Linux: nano .env
```

4. **Run the application**
```bash
python main.py
```

## Features

### Core Functionality
- **Dual Mode**: Works offline or with AI-powered GPT-4o integration
- **Smart Progress Tracking**: SQLite database with spaced repetition
- **Comprehensive Coverage**: All major Spanish tenses and irregular verbs
- **Multiple Practice Modes**: Standard, Speed, Task-based, Story mode
- **Adaptive Learning**: Focuses on weak areas automatically

### Practice Options
- Free response or multiple choice input
- Speed mode for fluency building (1-10 second timers)
- Story mode for connected discourse practice
- Task-based scenarios for real-world application
- Custom practice creator for targeted study

### Learning Tools
- Detailed statistics and progress tracking
- Spaced repetition algorithm for optimal retention
- AI-powered hints and explanations
- Quick verb reference charts
- Export progress and settings for backup

## Configuration

### Getting an OpenAI API Key (Optional)

1. Visit [OpenAI Platform](https://platform.openai.com)
2. Sign up or log in
3. Go to API Keys section
4. Create new secret key
5. Copy and paste into `.env` file

### Offline Mode

The app works completely offline with:
- 100+ built-in verbs
- Local exercise generation
- Full progress tracking
- No API key required

## Usage Guide

### First Time Setup

1. **Launch the app**
   - Windows: Double-click `SpanishConjugation.exe`
   - From source: Run `python main.py`

2. **Configure practice options**
   - Select tenses (Present, Preterite, Imperfect, etc.)
   - Choose persons (yo, tú, él/ella, etc.)
   - Set difficulty level
   - Optionally specify verbs or themes

3. **Start practicing**
   - Click "New Exercise" to begin
   - Type or select your answer
   - Get instant feedback
   - Track your progress

### Practice Modes

#### Standard Practice
- Customizable exercises by tense/person
- Theme-based vocabulary
- Three difficulty levels

#### Speed Mode
- Timed responses (1-10 seconds)
- Build conversational fluency
- Track response times

#### Task Mode
- Real-world scenarios
- Communicative goals
- Practical applications

#### Story Mode
- Connected narratives
- Contextual learning
- Progressive difficulty

## Building from Source

### Create Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
python build_exe.py

# Find executable in dist/ folder
```

### Development Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
```

## Project Structure

```
conjugation_gui/
├── main.py                 # Main application
├── conjugation_engine.py   # Verb conjugation logic
├── exercise_generator.py   # Exercise creation
├── progress_tracker.py     # Database and progress
├── task_scenarios.py       # Task-based learning
├── speed_practice.py       # Speed mode
├── learning_path.py        # Learning progression
├── requirements.txt        # Python dependencies
├── .env.example           # API key template
├── build_exe.py           # Build script
└── README.md              # This file
```

## Troubleshooting

### Common Issues

**"No module named 'PyQt5'"**
```bash
pip install PyQt5==5.15.7
```

**"OPENAI_API_KEY not found"**
- Create `.env` file from `.env.example`
- Add your API key or use offline mode

**Application won't start on Mac**
```bash
# May need to allow in Security settings
xattr -cr SpanishConjugation.app
```

**Database errors**
- Delete `progress.db` to reset progress
- Check write permissions in app directory

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### How to Contribute

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## System Requirements

### Minimum
- **OS**: Windows 10, macOS 10.14, Ubuntu 20.04
- **RAM**: 2GB
- **Storage**: 100MB
- **Python**: 3.8+

### Recommended
- **RAM**: 4GB
- **Internet**: For AI features
- **Display**: 1920x1080

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with PyQt5
- Powered by OpenAI GPT-4o (optional)
- Spanish conjugation rules from RAE
- Community contributors

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/conjugation_gui/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/conjugation_gui/discussions)
- **Email**: your.email@example.com

## Roadmap

- Voice input/output for pronunciation practice
- Mobile companion app for learning on the go
- Additional language support
- Cloud sync for cross-device progress
- Gamification features for engagement

## Exploring the Code

The project demonstrates desktop application development with Python and PyQt5:

```
conjugation_gui/
├── main.py                 # Application entry point and UI
├── conjugation_engine.py   # Verb conjugation logic
├── exercise_generator.py   # Exercise creation algorithms
├── progress_tracker.py     # SQLite database management
├── task_scenarios.py       # Real-world task scenarios
├── speed_practice.py       # Timed practice mode
├── learning_path.py        # Adaptive learning progression
└── build_exe.py            # PyInstaller build script
```

**Architecture Highlights:**
- PyQt5 for cross-platform desktop UI
- SQLite for local progress persistence
- Optional OpenAI integration for AI-powered features
- Spaced repetition algorithm for optimized learning
- Modular design separating UI from business logic

**For Technical Review:**

Those interested in the implementation details can explore:
- `conjugation_engine.py` for Spanish verb conjugation rules
- `progress_tracker.py` for spaced repetition implementation
- `exercise_generator.py` for dynamic exercise creation
- `learning_path.py` for adaptive difficulty algorithms

---

Built for Spanish learners worldwide